"""Download checkpoints directly from DagsHub S3 storage.

Bypasses DVC entirely to avoid filesystem issues on platforms like Render
where /var/tmp is read-only. Uses boto3 (installed via dvc-s3 dependency)
for proper S3 SigV4 authentication with DagsHub.

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
from pathlib import Path

import boto3

# DagsHub S3 configuration (matches .dvc/config)
ENDPOINT_URL = "https://dagshub.com/akksel1/final_project.s3"
BUCKET = "dvc"

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHECKPOINTS_DIR = PROJECT_ROOT / "checkpoints"
DVC_FILE = PROJECT_ROOT / "checkpoints.dvc"


def md5_to_s3_key(md5_hash: str) -> str:
    """Convert an MD5 hash to the DVC S3 storage key."""
    return f"files/md5/{md5_hash[:2]}/{md5_hash[2:]}"


def main():
    key = os.environ.get("AWS_ACCESS_KEY_ID", "")
    secret = os.environ.get("AWS_SECRET_ACCESS_KEY", "")

    if not key or not secret:
        print("❌ AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY not set")
        print("   Set them to your DagsHub token.")
        sys.exit(1)

    # Parse checkpoints.dvc (regex, no pyyaml needed)
    if not DVC_FILE.exists():
        print(f"❌ {DVC_FILE} not found")
        sys.exit(1)

    dvc_content = DVC_FILE.read_text()
    md5_match = re.search(r"md5:\s+(\w+)\.dir", dvc_content)
    if not md5_match:
        print("❌ Could not parse directory hash from checkpoints.dvc")
        sys.exit(1)

    dir_md5 = md5_match.group(1)
    print(f"🔗 Directory hash: {dir_md5}")

    # Create S3 client for DagsHub
    s3 = boto3.client(
        "s3",
        endpoint_url=ENDPOINT_URL,
        aws_access_key_id=key,
        aws_secret_access_key=secret,
    )

    # Step 1: Download the .dir manifest (JSON listing all files + hashes)
    manifest_key = md5_to_s3_key(dir_md5 + ".dir")
    print("📋 Downloading manifest...")

    response = s3.get_object(Bucket=BUCKET, Key=manifest_key)
    file_entries = json.loads(response["Body"].read().decode("utf-8"))
    print(f"   Found {len(file_entries)} file(s)")

    # Step 2: Download each file
    CHECKPOINTS_DIR.mkdir(parents=True, exist_ok=True)

    for entry in file_entries:
        relpath = entry["relpath"]
        file_md5 = entry["md5"]
        s3_key = md5_to_s3_key(file_md5)
        local_path = CHECKPOINTS_DIR / relpath
        local_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"  📥 Downloading {relpath}...")
        s3.download_file(BUCKET, s3_key, str(local_path))

        # Verify MD5
        actual_md5 = hashlib.md5(local_path.read_bytes()).hexdigest()
        if actual_md5 != file_md5:
            print(f"  ⚠️ MD5 mismatch: expected {file_md5}, got {actual_md5}")
        else:
            print(f"  ✅ {relpath} ({local_path.stat().st_size:,} bytes)")

    total = sum((CHECKPOINTS_DIR / e["relpath"]).stat().st_size for e in file_entries)
    print(f"\n✅ Downloaded {len(file_entries)} files ({total / 1024 / 1024:.1f} MB)")


if __name__ == "__main__":
    main()
