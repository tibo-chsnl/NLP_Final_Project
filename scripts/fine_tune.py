#!/usr/bin/env python
"""
Fine-tune the existing QA model on a small data sample + new feedback.

Designed to run on GitHub Actions free-tier (2 CPU, 7GB RAM, 6h limit).
Loads the current best model weights from local checkpoints (downloaded via
DVC or download_checkpoints.py), trains for a few epochs on 10% of the
original data plus 100% of any new user-feedback examples, then uploads
the improved model to MLflow/DagsHub.

Usage:
    # Fine-tune with defaults (10% sample, 2 epochs)
    uv run python scripts/fine_tune.py

    # Custom sample ratio and epochs
    uv run python scripts/fine_tune.py --sample-ratio 0.15 --epochs 3

    # Dry-run: just print what would happen
    uv run python scripts/fine_tune.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from pathlib import Path

import torch
import torch.nn as nn
from tqdm import tqdm

# Ensure project root is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from model.qa_model import QAModel  # noqa: E402
from src.data.loader import load_squad  # noqa: E402
from src.training.dataset import create_dataloader  # noqa: E402
from src.training.trainer import evaluate  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHECKPOINT_DIR = PROJECT_ROOT / "checkpoints"


def load_existing_model(device: torch.device) -> tuple[QAModel, dict[str, int], dict]:
    """Load the current best model, vocab, and config from checkpoints/."""
    config_path = CHECKPOINT_DIR / "config.json"
    weights_path = CHECKPOINT_DIR / "best_model.pt"
    vocab_path = CHECKPOINT_DIR / "vocab.json"

    for path in (config_path, weights_path, vocab_path):
        if not path.exists():
            print(f"❌ Missing checkpoint file: {path}")
            print("   Run `uv run dvc pull` or `uv run python scripts/download_checkpoints.py`")
            sys.exit(1)

    with open(config_path) as f:
        config = json.load(f)
    with open(vocab_path) as f:
        vocab = json.load(f)

    model = QAModel(
        vocab_size=config["vocab_size"],
        embedding_dim=config["embedding_dim"],
        hidden_dim=config["hidden_dim"],
        dropout=config.get("dropout", 0.2),
    )
    model.load_state_dict(torch.load(weights_path, map_location=device, weights_only=True))
    model.to(device)

    print(
        f"✅ Loaded existing model: {config['vocab_size']} vocab, "
        f"{config['embedding_dim']}d embed, {config['hidden_dim']}d hidden"
    )

    return model, vocab, config


def sample_examples(examples: list, ratio: float, seed: int = 42) -> list:
    """Randomly sample a fraction of examples."""
    rng = random.Random(seed)
    n = max(1, int(len(examples) * ratio))
    return rng.sample(examples, min(n, len(examples)))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Fine-tune the QA model on sampled data + feedback.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--train-path",
        type=str,
        default="data/train-v2.0.json",
        help="Path to the SQuAD training data (may include augmented feedback).",
    )
    parser.add_argument(
        "--dev-path",
        type=str,
        default="data/dev-v2.0.json",
        help="Path to the SQuAD dev data for validation.",
    )
    parser.add_argument(
        "--sample-ratio",
        type=float,
        default=0.10,
        help="Fraction of original training data to use (0.10 = 10%%).",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=2,
        help="Number of fine-tuning epochs.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=16,
        help="Training batch size.",
    )
    parser.add_argument(
        "--lr",
        type=float,
        default=0.0003,
        help="Learning rate (lower than full training for fine-tuning).",
    )
    parser.add_argument(
        "--max-context-len",
        type=int,
        default=400,
        help="Maximum context length in tokens.",
    )
    parser.add_argument(
        "--max-question-len",
        type=int,
        default=60,
        help="Maximum question length in tokens.",
    )
    parser.add_argument(
        "--save-dir",
        type=str,
        default="checkpoints",
        help="Directory to save fine-tuned checkpoints.",
    )
    parser.add_argument(
        "--experiment-name",
        type=str,
        default="QA_Model_FineTuning",
        help="MLflow experiment name.",
    )
    parser.add_argument(
        "--no-mlflow",
        action="store_true",
        help="Disable MLflow logging.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print plan without training.",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        help="Device to use (auto-detected if not set).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for data sampling.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    device = (
        torch.device(args.device)
        if args.device
        else torch.device("cuda" if torch.cuda.is_available() else "cpu")
    )
    print(f"🖥️  Device: {device}")

    # --- Load existing model ---
    model, vocab, config = load_existing_model(device)

    # --- Load and sample training data ---
    print(f"\n📂 Loading training data from {args.train_path}...")
    train_ds = load_squad(args.train_path)
    all_answerable = train_ds.answerable
    sampled = sample_examples(all_answerable, args.sample_ratio, seed=args.seed)

    print(f"   Total answerable: {len(all_answerable)}")
    print(f"   Sampled ({args.sample_ratio:.0%}): {len(sampled)}")

    # --- Load validation data ---
    print(f"📂 Loading dev data from {args.dev_path}...")
    dev_ds = load_squad(args.dev_path)
    print(f"   Dev answerable: {len(dev_ds.answerable)}")

    if args.dry_run:
        print("\n🏁 Dry run — would fine-tune with:")
        print(f"   Training samples: {len(sampled)}")
        print(f"   Epochs: {args.epochs}")
        print(f"   Batch size: {args.batch_size}")
        print(f"   Learning rate: {args.lr}")
        print(f"   Device: {device}")
        return

    # --- Create DataLoaders ---
    train_loader = create_dataloader(
        sampled,
        vocab,
        batch_size=args.batch_size,
        shuffle=True,
        max_context_len=args.max_context_len,
        max_question_len=args.max_question_len,
    )
    val_loader = create_dataloader(
        dev_ds.answerable,
        vocab,
        batch_size=args.batch_size,
        shuffle=False,
        max_context_len=args.max_context_len,
        max_question_len=args.max_question_len,
    )

    # --- MLflow setup ---
    mlflow = None
    use_mlflow = not args.no_mlflow
    if use_mlflow:
        try:
            import mlflow as _mlflow

            from src.tracking.mlflow_setup import init_tracking

            init_tracking(experiment_name=args.experiment_name)
            os.environ.pop("MLFLOW_RUN_ID", None)
            mlflow = _mlflow
        except Exception as e:
            print(f"⚠️  MLflow init failed: {e}. Continuing without tracking.")
            mlflow = None

    # --- Evaluate baseline before fine-tuning ---
    print("\n📊 Evaluating baseline (before fine-tuning)...")
    baseline_loss, baseline_f1, baseline_em = evaluate(model, val_loader, device, vocab=vocab)
    print(
        f"   Baseline — val_loss: {baseline_loss:.4f}, "
        f"val_f1: {baseline_f1:.4f}, val_em: {baseline_em:.4f}"
    )

    # --- Fine-tuning loop ---
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    loss_fn = nn.CrossEntropyLoss()

    os.makedirs(args.save_dir, exist_ok=True)
    best_f1 = baseline_f1
    history = []

    run_context = mlflow.start_run(run_name="fine-tune") if mlflow else None
    if mlflow:
        mlflow.log_params(
            {
                "fine_tune": True,
                "sample_ratio": args.sample_ratio,
                "epochs": args.epochs,
                "batch_size": args.batch_size,
                "learning_rate": args.lr,
                "train_samples": len(train_loader.dataset),
                "val_samples": len(val_loader.dataset),
                "baseline_f1": round(baseline_f1, 4),
                "baseline_em": round(baseline_em, 4),
                "device": str(device),
            }
        )

    try:
        for epoch in range(args.epochs):
            model.train()
            running_loss = 0.0
            num_batches = 0

            pbar = tqdm(train_loader, desc=f"Fine-tune {epoch + 1}/{args.epochs}", leave=True)
            for batch in pbar:
                context_ids = batch["context_ids"].to(device)
                question_ids = batch["question_ids"].to(device)
                context_mask = batch["context_mask"].to(device)
                question_mask = batch["question_mask"].to(device)
                start_idx = batch["start_idx"].to(device)
                end_idx = batch["end_idx"].to(device)

                optimizer.zero_grad()

                start_logits, end_logits = model(
                    context=context_ids,
                    query=question_ids,
                    context_mask=context_mask,
                    query_mask=question_mask,
                )

                loss_start = loss_fn(start_logits, start_idx)
                loss_end = loss_fn(end_logits, end_idx)
                loss = (loss_start + loss_end) / 2

                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
                optimizer.step()

                running_loss += loss.item()
                num_batches += 1
                pbar.set_postfix(loss=f"{running_loss / num_batches:.4f}")

            train_loss = running_loss / max(num_batches, 1)
            val_loss, val_f1, val_em = evaluate(model, val_loader, device, vocab=vocab)

            epoch_info = {
                "epoch": epoch + 1,
                "train_loss": round(train_loss, 4),
                "val_loss": round(val_loss, 4),
                "val_f1": round(val_f1, 4),
                "val_em": round(val_em, 4),
            }
            history.append(epoch_info)
            print(
                f"Fine-tune {epoch + 1}/{args.epochs} — "
                f"train_loss: {train_loss:.4f} — "
                f"val_loss: {val_loss:.4f} — "
                f"val_f1: {val_f1:.4f} — "
                f"val_em: {val_em:.4f}"
            )

            if mlflow:
                mlflow.log_metrics(
                    {
                        "train_loss": train_loss,
                        "val_loss": val_loss,
                        "val_f1": val_f1,
                        "val_em": val_em,
                    },
                    step=epoch + 1,
                )

            # Only save if we improved over the baseline
            if val_f1 > best_f1:
                best_f1 = val_f1
                torch.save(model.state_dict(), os.path.join(args.save_dir, "best_model.pt"))

                vocab_path = os.path.join(args.save_dir, "vocab.json")
                config_path = os.path.join(args.save_dir, "config.json")
                with open(vocab_path, "w") as f:
                    json.dump(vocab, f)
                with open(config_path, "w") as f:
                    json.dump(config, f)

                if mlflow:
                    mlflow.pytorch.log_model(
                        model,
                        artifact_path="qa-model",
                        registered_model_name="QA_Model",
                    )
                    mlflow.log_artifact(vocab_path, artifact_path="qa-model")
                    mlflow.log_artifact(config_path, artifact_path="qa-model")
                    print(f"  📦 Improved model uploaded to MLflow (val_f1={val_f1:.4f})")

        # --- Summary ---
        improved = best_f1 > baseline_f1
        print(f"\n{'✅' if improved else '⚠️'}  Fine-tuning complete.")
        print(f"   Baseline F1: {baseline_f1:.4f}")
        print(f"   Best F1:     {best_f1:.4f}")
        print(f"   {'Improved!' if improved else 'No improvement — keeping original model.'}")

        if mlflow:
            mlflow.log_metrics(
                {
                    "best_val_f1": best_f1,
                    "baseline_f1": baseline_f1,
                    "improved": float(improved),
                }
            )

            if history:
                history_path = os.path.join(args.save_dir, "finetune_history.json")
                with open(history_path, "w") as f:
                    json.dump(history, f, indent=2)
                mlflow.log_artifact(history_path)

    finally:
        if mlflow and run_context:
            mlflow.end_run()


if __name__ == "__main__":
    main()
