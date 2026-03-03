#!/usr/bin/env python
"""
Training entrypoint script for the QA model.

Initialises DagsHub/MLflow tracking, then launches a full training run.
All hyperparameters can be overridden through CLI arguments.

Usage:
    python scripts/train.py --epochs 3 --batch-size 16 --lr 0.001
"""

import argparse
import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.tracking.mlflow_setup import init_tracking
from src.training.trainer import train


def parse_args():
    parser = argparse.ArgumentParser(
        description="Train the BiDAF QA model and upload to DagsHub via MLflow.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Data paths
    parser.add_argument(
        "--train-path",
        type=str,
        default="data/train-v2.0.json",
        help="Path to SQuAD training JSON file.",
    )
    parser.add_argument(
        "--dev-path",
        type=str,
        default="data/dev-v2.0.json",
        help="Path to SQuAD dev/validation JSON file.",
    )

    # Hyperparameters
    parser.add_argument("--epochs", type=int, default=5, help="Number of training epochs.")
    parser.add_argument(
        "--batch-size", type=int, default=32, help="Batch size for training and validation."
    )
    parser.add_argument("--lr", type=float, default=0.001, help="Learning rate for Adam optimizer.")
    parser.add_argument(
        "--hidden-dim", type=int, default=128, help="Hidden dimension for LSTM layers."
    )
    parser.add_argument(
        "--embedding-dim", type=int, default=100, help="Dimension of word embeddings."
    )
    parser.add_argument("--dropout", type=float, default=0.2, help="Dropout probability.")
    parser.add_argument(
        "--max-context-len", type=int, default=400, help="Maximum context sequence length (tokens)."
    )
    parser.add_argument(
        "--max-question-len",
        type=int,
        default=60,
        help="Maximum question sequence length (tokens).",
    )
    parser.add_argument(
        "--min-freq", type=int, default=2, help="Minimum token frequency to include in vocabulary."
    )
    parser.add_argument(
        "--max-vocab-size", type=int, default=50000, help="Maximum vocabulary size."
    )

    # Output
    parser.add_argument(
        "--save-dir", type=str, default="checkpoints", help="Directory to save model checkpoints."
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        help="Device to train on (e.g. 'cpu', 'cuda'). Auto-detected if omitted.",
    )

    # MLflow / DagsHub
    parser.add_argument(
        "--experiment-name",
        type=str,
        default="QA_Model_Training",
        help="MLflow experiment name on DagsHub.",
    )
    parser.add_argument(
        "--no-mlflow", action="store_true", help="Disable MLflow tracking (local-only training)."
    )

    return parser.parse_args()


def main():
    args = parse_args()

    # --- Initialise DagsHub + MLflow tracking ---
    use_mlflow = not args.no_mlflow
    if use_mlflow:
        print("=" * 60)
        print("  🚀 Initialising DagsHub / MLflow tracking")
        print("=" * 60)
        init_tracking(experiment_name=args.experiment_name)
        # Prevent mlflow.start_run() from resuming an existing run when training
        os.environ.pop("MLFLOW_RUN_ID", None)
    else:
        print("⚠️  MLflow tracking disabled (--no-mlflow). Training locally only.")

    # --- Launch training ---
    print("\n" + "=" * 60)
    print("  🏋️  Starting training")
    print("=" * 60)

    model, vocab, history = train(
        train_path=args.train_path,
        dev_path=args.dev_path,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        hidden_dim=args.hidden_dim,
        embedding_dim=args.embedding_dim,
        dropout=args.dropout,
        max_context_len=args.max_context_len,
        max_question_len=args.max_question_len,
        min_freq=args.min_freq,
        max_vocab_size=args.max_vocab_size,
        save_dir=args.save_dir,
        device=args.device,
        use_mlflow=use_mlflow,
    )

    # --- Summary ---
    print("\n" + "=" * 60)
    print("  ✅ Training complete!")
    print("=" * 60)
    best_epoch = max(history, key=lambda h: h["val_f1"])
    print(f"  Best epoch : {best_epoch['epoch']}")
    print(f"  Best val_f1: {best_epoch['val_f1']:.4f}")
    print(f"  Best val_em: {best_epoch['val_em']:.4f}")
    print(f"  Checkpoints: {args.save_dir}/")
    if use_mlflow:
        print("  📊 View results on DagsHub MLflow Experiments tab")


if __name__ == "__main__":
    main()
