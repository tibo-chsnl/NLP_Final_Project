import json
import os

import torch
import torch.nn as nn
from tqdm import tqdm

from model.qa_model import QAModel
from src.data.loader import load_squad
from src.evaluation.metrics import compute_exact_match, compute_f1
from src.training.dataset import build_vocab_from_dataset, create_dataloader


def evaluate(model, dataloader, device, vocab=None):
    model.eval()
    total_loss = 0
    total_f1 = 0
    total_em = 0
    count = 0
    loss_fn = nn.CrossEntropyLoss()

    idx_to_word = None
    if vocab:
        idx_to_word = {v: k for k, v in vocab.items()}

    with torch.no_grad():
        for batch in tqdm(dataloader, desc="  Evaluating", leave=False):
            context_ids = batch["context_ids"].to(device)
            question_ids = batch["question_ids"].to(device)
            context_mask = batch["context_mask"].to(device)
            question_mask = batch["question_mask"].to(device)
            start_idx = batch["start_idx"].to(device)
            end_idx = batch["end_idx"].to(device)

            start_logits, end_logits = model(
                context=context_ids,
                query=question_ids,
                context_mask=context_mask,
                query_mask=question_mask,
            )

            loss_start = loss_fn(start_logits, start_idx)
            loss_end = loss_fn(end_logits, end_idx)
            loss = (loss_start + loss_end) / 2
            total_loss += loss.item()

            pred_starts = torch.argmax(start_logits, dim=1)
            pred_ends = torch.argmax(end_logits, dim=1)

            for i in range(context_ids.size(0)):
                c_len = context_mask[i].sum().item()
                c_ids = context_ids[i][:c_len].tolist()

                ps = pred_starts[i].item()
                pe = pred_ends[i].item()
                gs = start_idx[i].item()
                ge = end_idx[i].item()

                pred_tokens = c_ids[ps : max(ps, pe) + 1]
                gold_tokens = c_ids[gs : ge + 1]

                if idx_to_word:
                    pred_text = " ".join(idx_to_word.get(t, "<UNK>") for t in pred_tokens)
                    gold_text = " ".join(idx_to_word.get(t, "<UNK>") for t in gold_tokens)
                else:
                    pred_text = " ".join(str(t) for t in pred_tokens)
                    gold_text = " ".join(str(t) for t in gold_tokens)

                total_f1 += compute_f1(pred_text, gold_text)
                total_em += compute_exact_match(pred_text, gold_text)
                count += 1

    avg_loss = total_loss / max(len(dataloader), 1)
    avg_f1 = total_f1 / max(count, 1)
    avg_em = total_em / max(count, 1)
    return avg_loss, avg_f1, avg_em


def train(
    train_path="data/train-v2.0.json",
    dev_path="data/dev-v2.0.json",
    epochs=5,
    batch_size=32,
    lr=0.001,
    hidden_dim=128,
    embedding_dim=100,
    dropout=0.2,
    max_context_len=400,
    max_question_len=60,
    min_freq=2,
    max_vocab_size=50000,
    save_dir="checkpoints",
    device=None,
    use_mlflow=False,
):
    # --- Optional MLflow import ---
    mlflow = None
    if use_mlflow:
        import mlflow as _mlflow

        mlflow = _mlflow

    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(device)

    # --- Load data ---
    train_ds = load_squad(train_path)
    dev_ds = load_squad(dev_path)

    vocab = build_vocab_from_dataset(train_ds, min_freq=min_freq, max_size=max_vocab_size)

    train_loader = create_dataloader(
        train_ds.answerable,
        vocab,
        batch_size=batch_size,
        shuffle=True,
        max_context_len=max_context_len,
        max_question_len=max_question_len,
    )
    val_loader = create_dataloader(
        dev_ds.answerable,
        vocab,
        batch_size=batch_size,
        shuffle=False,
        max_context_len=max_context_len,
        max_question_len=max_question_len,
    )

    # --- Build model ---
    model = QAModel(
        vocab_size=len(vocab),
        embedding_dim=embedding_dim,
        hidden_dim=hidden_dim,
        dropout=dropout,
    )
    model.to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.CrossEntropyLoss()

    os.makedirs(save_dir, exist_ok=True)
    best_f1 = 0.0
    history = []

    # --- MLflow: start run & log hyperparameters ---
    run_context = mlflow.start_run() if mlflow else None
    if mlflow:
        mlflow.log_params(
            {
                "epochs": epochs,
                "batch_size": batch_size,
                "learning_rate": lr,
                "hidden_dim": hidden_dim,
                "embedding_dim": embedding_dim,
                "dropout": dropout,
                "max_context_len": max_context_len,
                "max_question_len": max_question_len,
                "min_freq": min_freq,
                "max_vocab_size": max_vocab_size,
                "vocab_size": len(vocab),
                "train_samples": len(train_loader.dataset),
                "val_samples": len(val_loader.dataset),
                "device": str(device),
            }
        )

    try:
        for epoch in range(epochs):
            model.train()
            running_loss = 0.0
            num_batches = 0

            pbar = tqdm(train_loader, desc=f"Epoch {epoch + 1}/{epochs}", leave=True)
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
                f"Epoch {epoch + 1}/{epochs} — "
                f"train_loss: {train_loss:.4f} — "
                f"val_loss: {val_loss:.4f} — "
                f"val_f1: {val_f1:.4f} — "
                f"val_em: {val_em:.4f}"
            )

            # --- MLflow: log epoch metrics ---
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

            if val_f1 > best_f1:
                best_f1 = val_f1
                torch.save(model.state_dict(), os.path.join(save_dir, "best_model.pt"))

                # Save vocab & config locally
                vocab_path = os.path.join(save_dir, "vocab.json")
                config_path = os.path.join(save_dir, "config.json")
                with open(vocab_path, "w") as f:
                    json.dump(vocab, f)
                with open(config_path, "w") as f:
                    json.dump(
                        {
                            "vocab_size": len(vocab),
                            "embedding_dim": embedding_dim,
                            "hidden_dim": hidden_dim,
                            "dropout": dropout,
                        },
                        f,
                    )

                # --- MLflow: log model + artifacts on best F1 ---
                if mlflow:
                    mlflow.pytorch.log_model(
                        model, artifact_path="qa-model", registered_model_name="QA_Model"
                    )
                    mlflow.log_artifact(vocab_path, artifact_path="qa-model")
                    mlflow.log_artifact(config_path, artifact_path="qa-model")
                    print(f"  📦 Model uploaded and registered to MLflow (val_f1={val_f1:.4f})")

        torch.save(model.state_dict(), os.path.join(save_dir, "last_model.pt"))

        with open(os.path.join(save_dir, "history.json"), "w") as f:
            json.dump(history, f, indent=2)

        # --- MLflow: log final summary metrics ---
        if mlflow:
            best_epoch = max(history, key=lambda h: h["val_f1"])
            mlflow.log_metrics(
                {
                    "best_val_f1": best_epoch["val_f1"],
                    "best_val_em": best_epoch["val_em"],
                    "best_epoch": best_epoch["epoch"],
                }
            )
            mlflow.log_artifact(os.path.join(save_dir, "history.json"))
            print(f"\n✅ MLflow run completed. Best val_f1: {best_epoch['val_f1']:.4f}")

    finally:
        # Ensure the MLflow run is always closed
        if mlflow and run_context:
            mlflow.end_run()

    return model, vocab, history


if __name__ == "__main__":
    train()
