"""Download checkpoints directly from DagsHub S3 storage.

Bypasses DVC entirely to avoid filesystem issues on platforms like Render
where /var/tmp is read-only. Uses only stdlib (no boto3/pyyaml required).

Usage:
    python scripts/download_checkpoints.py

Requires env vars:
    AWS_ACCESS_KEY_ID     = DagsHub token
    AWS_SECRET_ACCESS_KEY = DagsHub token
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import urllib.request
from base64 import b64encode
from pathlib import Path

# DagsHub S3 configuration (matches .dvc/config)
DAGSHUB_STORAGE = "https://dagshub.com/akksel1/final_project.s3"
BUCKET = "dvc"

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHECKPOINTS_DIR = PROJECT_ROOT / "checkpoints"
DVC_FILE = PROJECT_ROOT / "checkpoints.dvc"


def md5_to_s3_path(md5_hash: str) -> str:
    """Convert an MD5 hash to the DVC S3 storage path."""
    return f"files/md5/{md5_hash[:2]}/{md5_hash[2:]}"


def download(url: str, dest: Path, token: str) -> None:
    """Download a file from DagsHub S3 using Basic auth."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    credentials = b64encode(f"{token}:{token}".encode()).decode()
    req = urllib.request.Request(url, headers={"Authorization": f"Basic {credentials}"})
    with urllib.request.urlopen(req) as resp, open(dest, "wb") as f:
        f.write(resp.read())


def main():
    token = os.environ.get("AWS_ACCESS_KEY_ID", "")
    if not token:
        print("❌ AWS_ACCESS_KEY_ID not set (should be your DagsHub token)")
        sys.exit(1)

    # Parse checkpoints.dvc (simple enough to regex, no pyyaml needed)
    if not DVC_FILE.exists():
        print(f"❌ {DVC_FILE} not found")
        sys.exit(1)

    dvc_content = DVC_FILE.read_text()
    md5_match = re.search(r"md5:\s+(\w+\.dir)", dvc_content)
    if not md5_match:
        print("❌ Could not parse directory hash from checkpoints.dvc")
        sys.exit(1)

    dir_md5 = md5_match.group(1).replace(".dir", "")
    print(f"🔗 Directory hash: {dir_md5}")

    # Step 1: Download the .dir manifest (JSON listing all files + hashes)
    manifest_path = md5_to_s3_path(dir_md5 + ".dir")
    manifest_url = f"{DAGSHUB_STORAGE}/{BUCKET}/{manifest_path}"
    tmp_manifest = Path("/tmp/dvc_manifest.json")

    print("📋 Downloading manifest...")
    download(manifest_url, tmp_manifest, token)

    file_entries = json.loads(tmp_manifest.read_text())
    tmp_manifest.unlink()
    print(f"   Found {len(file_entries)} file(s)")

    # Step 2: Download each file
    CHECKPOINTS_DIR.mkdir(parents=True, exist_ok=True)

    for entry in file_entries:
        relpath = entry["relpath"]
        file_md5 = entry["md5"]
        file_path = md5_to_s3_path(file_md5)
        file_url = f"{DAGSHUB_STORAGE}/{BUCKET}/{file_path}"
        local_path = CHECKPOINTS_DIR / relpath

        print(f"  📥 Downloading {relpath}...")
        download(file_url, local_path, token)

        # Verify MD5
        actual_md5 = hashlib.md5(local_path.read_bytes()).hexdigest()
        if actual_md5 != file_md5:
            print(f"  ⚠️ MD5 mismatch: expected {file_md5}, got {actual_md5}")
        else:
            print(f"  ✅ {relpath} verified ({local_path.stat().st_size:,} bytes)")

    total_size = sum((CHECKPOINTS_DIR / e["relpath"]).stat().st_size for e in file_entries)
    print(
        f"\n✅ Downloaded {len(file_entries)} files"
        f" ({total_size / 1024 / 1024:.1f} MB) to {CHECKPOINTS_DIR}"
    )


if __name__ == "__main__":
    main()
