"""Pull user feedback from Supabase and augment the training dataset.

Reads corrected QA triplets submitted by users through the frontend,
converts them into SQuAD format, and appends them to the training data.
Processed rows are marked so they are not pulled again.

Usage:
    uv run python scripts/pull_feedback.py
    uv run python scripts/pull_feedback.py --dataset data/train-v2.0.json --dry-run
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

# Ensure project root is on the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data.augmentation import augment_from_triplets  # noqa: E402


def get_supabase_client():
    """Create and return a Supabase client using environment variables."""
    try:
        from supabase import create_client
    except ImportError:
        print("❌ supabase-py is not installed. Run: uv add supabase")
        sys.exit(1)

    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_KEY", "") or os.environ.get("SUPABASE_KEY", "")

    if not url or not key:
        print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in environment.")
        print("   Set them in your .env file. See .env.example for reference.")
        sys.exit(1)

    return create_client(url, key)


def fetch_unprocessed_feedback(client) -> list[dict]:
    """Fetch all feedback rows that haven't been processed yet.

    Only retrieves negative feedback (positive=false) where the user
    provided a corrected answer — these are the useful training signals.
    """
    response = (
        client.table("feedback")
        .select("id, context, question, answer, original_answer, positive")
        .eq("processed", False)
        .eq("positive", False)  # Only corrections, not validations
        .execute()
    )

    return response.data or []


def mark_as_processed(client, row_ids: list[str]) -> None:
    """Mark feedback rows as processed so they won't be pulled again."""
    if not row_ids:
        return

    now = datetime.now(timezone.utc).isoformat()

    client.table("feedback").update({"processed": True, "processed_at": now}).in_(
        "id", row_ids
    ).execute()


def convert_to_triplets(feedback_rows: list[dict]) -> list[dict[str, str]]:
    """Convert Supabase feedback rows to the triplet format expected by augmentation.

    Uses the user-corrected 'answer' (not the model's 'original_answer').
    """
    triplets = []
    skipped = 0

    for row in feedback_rows:
        context = (row.get("context") or "").strip()
        question = (row.get("question") or "").strip()
        answer = (row.get("answer") or "").strip()

        # Validate: answer must exist in context (required for SQuAD format)
        if not context or not question or not answer:
            skipped += 1
            continue

        if answer.lower() not in context.lower():
            print(f"  ⚠️  Skipping row {row['id']}: answer not found in context")
            skipped += 1
            continue

        triplets.append(
            {
                "context": context,
                "question": question,
                "answer": answer,
            }
        )

    if skipped:
        print(f"  ℹ️  Skipped {skipped} invalid row(s)")

    return triplets


def main():
    parser = argparse.ArgumentParser(
        description="Pull user feedback from Supabase and augment training data."
    )
    parser.add_argument(
        "--dataset",
        default="data/train-v2.0.json",
        help="Path to the SQuAD training JSON to augment (default: data/train-v2.0.json)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output path for augmented dataset (default: overwrite original)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch and display feedback without modifying the dataset or marking rows",
    )
    args = parser.parse_args()

    # Load .env from project root
    project_root = Path(__file__).resolve().parent.parent
    load_dotenv(project_root / ".env")

    dataset_path = Path(args.dataset)
    if not dataset_path.exists():
        print(f"❌ Dataset not found: {dataset_path}")
        print("   Run `uv run dvc pull` to download the training data first.")
        sys.exit(1)

    # Step 1: Connect to Supabase
    print("🔗 Connecting to Supabase...")
    client = get_supabase_client()

    # Step 2: Fetch unprocessed negative feedback
    print("📥 Fetching unprocessed feedback...")
    feedback_rows = fetch_unprocessed_feedback(client)

    if not feedback_rows:
        print("✅ No new feedback to process. Dataset is up to date.")
        return

    print(f"   Found {len(feedback_rows)} new correction(s)")

    # Step 3: Convert to SQuAD triplets
    print("🔄 Converting to SQuAD format...")
    triplets = convert_to_triplets(feedback_rows)

    if not triplets:
        print("⚠️  No valid triplets after filtering. Nothing to augment.")
        return

    print(f"   {len(triplets)} valid triplet(s) ready for augmentation")

    if args.dry_run:
        print("\n🔍 Dry run — preview of triplets that would be added:\n")
        for i, t in enumerate(triplets, 1):
            print(f"  [{i}] Q: {t['question']}")
            print(f"      A: {t['answer']}")
            print(f"      C: {t['context'][:100]}...")
            print()
        print("No changes made (--dry-run).")
        return

    # Step 4: Augment dataset
    print(f"📝 Augmenting dataset: {dataset_path}")
    output_path = augment_from_triplets(
        original_path=dataset_path,
        triplets=triplets,
        output_path=args.output,
    )
    print(f"   Saved to: {output_path}")

    # Step 5: Mark rows as processed
    print("✓  Marking feedback as processed...")
    row_ids = [row["id"] for row in feedback_rows]
    mark_as_processed(client, row_ids)

    print(f"\n✅ Done! Added {len(triplets)} new example(s) to the training dataset.")
    print("   Next steps:")
    print("   1. Review the augmented dataset")
    print("   2. Run `uv run dvc push` to sync the updated data")
    print("   3. Retrain the model with the augmented dataset")


if __name__ == "__main__":
    main()
