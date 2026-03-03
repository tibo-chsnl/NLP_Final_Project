import json
import os
from pathlib import Path
from typing import Any, Dict, Tuple

import torch

from model.qa_model import QAModel
from src.data.preprocessing import tokenize

CHECKPOINT_DIR = Path(__file__).resolve().parent.parent / "checkpoints"


class InferencePipeline:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.vocab: Dict[str, int] = {}
        self.vocab_size = 10000
        self.model = None
        self.is_dummy = True

        self._load_model()

    def _load_model(self):
        use_mlflow = os.environ.get("USE_MLFLOW", "false").lower() == "true"

        if use_mlflow:
            try:
                import tempfile

                import mlflow.artifacts

                from src.tracking.mlflow_setup import init_tracking

                init_tracking()

                model_name = os.environ.get("MLFLOW_MODEL_NAME", "QA_Model")
                model_alias = os.environ.get("MLFLOW_MODEL_ALIAS", "latest")
                model_uri = f"models:/{model_name}/{model_alias}"

                run_id = os.environ.get("MLFLOW_RUN_ID")
                if run_id:
                    model_uri = f"runs:/{run_id}/qa-model"

                print(f"⏳ Attempting to load model from MLflow: {model_uri}")
                self.model = mlflow.pytorch.load_model(model_uri)
                self.model.to(self.device)
                self.model.eval()

                with tempfile.TemporaryDirectory() as tmpdir:
                    try:
                        vocab_path_downloaded = mlflow.artifacts.download_artifacts(
                            artifact_uri=f"{model_uri}/vocab.json",
                            dst_path=tmpdir,
                        )
                        with open(vocab_path_downloaded) as f:
                            self.vocab = json.load(f)
                        self.vocab_size = len(self.vocab)
                    except Exception as e:
                        print(
                            f"⚠️ Failed to download vocab.json from MLflow,"
                            f" using fallback vocab: {e}"
                        )
                        self.vocab = {"<PAD>": 0, "<UNK>": 1}
                        self.vocab_size = 50000
                self.is_dummy = False
                print("✅ Successfully loaded model and vocab from MLflow!")
                return
            except Exception as e:
                print(f"⚠️ Failed to load model from MLflow: {e}")

        config_path = CHECKPOINT_DIR / "config.json"
        weights_path = CHECKPOINT_DIR / "best_model.pt"
        vocab_path = CHECKPOINT_DIR / "vocab.json"

        if config_path.exists() and weights_path.exists() and vocab_path.exists():
            with open(config_path) as f:
                config = json.load(f)
            with open(vocab_path) as f:
                self.vocab = json.load(f)

            self.vocab_size = config["vocab_size"]
            self.model = QAModel(
                vocab_size=config["vocab_size"],
                embedding_dim=config["embedding_dim"],
                hidden_dim=config["hidden_dim"],
                dropout=config.get("dropout", 0.0),
            )
            self.model.load_state_dict(
                torch.load(weights_path, map_location=self.device, weights_only=True)
            )
            self.model.to(self.device)
            self.model.eval()
            self.is_dummy = False
            return

        self.vocab = {"<PAD>": 0, "<UNK>": 1}
        self.vocab_size = 10000
        self.model = QAModel(
            vocab_size=self.vocab_size,
            embedding_dim=64,
            hidden_dim=64,
            dropout=0.0,
        )
        self.model.to(self.device)
        self.model.eval()
        self.is_dummy = True

    def _preprocess(
        self,
        context: str,
        question: str,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, list]:
        context_tokens = tokenize(context)
        question_tokens = tokenize(question)

        unk = self.vocab.get("<UNK>", 1)
        c_indices = [self.vocab.get(tok, unk) for tok in context_tokens]
        q_indices = [self.vocab.get(tok, unk) for tok in question_tokens]

        c_tensor = torch.tensor(c_indices, dtype=torch.long, device=self.device).unsqueeze(0)
        q_tensor = torch.tensor(q_indices, dtype=torch.long, device=self.device).unsqueeze(0)

        c_mask = torch.ones_like(c_tensor, dtype=torch.bool, device=self.device)
        q_mask = torch.ones_like(q_tensor, dtype=torch.bool, device=self.device)

        return c_tensor, q_tensor, c_mask, q_mask, context_tokens

    def _postprocess(
        self,
        start_logits: torch.Tensor,
        end_logits: torch.Tensor,
        context_tokens: list,
    ) -> Tuple[str, float]:
        start_logits = start_logits.squeeze(0)
        end_logits = end_logits.squeeze(0)

        max_len = len(context_tokens)
        start_logits = start_logits[:max_len]
        end_logits = end_logits[:max_len]

        start_idx = torch.argmax(start_logits).item()

        mask = torch.ones_like(end_logits) * -1e9
        max_span = min(30, max_len - start_idx)
        mask[start_idx : start_idx + max_span] = 0
        valid_end_logits = end_logits + mask
        end_idx = torch.argmax(valid_end_logits).item()

        answer_tokens = context_tokens[start_idx : end_idx + 1]
        answer = " ".join(answer_tokens)

        start_prob = torch.softmax(start_logits, dim=0)[start_idx].item()
        end_prob = torch.softmax(valid_end_logits, dim=0)[end_idx].item()
        confidence = (start_prob + end_prob) / 2.0

        if not answer.strip() or start_idx > end_idx:
            answer = "Unable to find a conclusive answer."
            confidence = 0.0

        return answer, confidence

    def predict(self, context: str, question: str) -> Dict[str, Any]:
        if not self.model:
            raise RuntimeError("Model is not initialized.")

        if not context.strip() or not question.strip():
            return {
                "answer": "Please provide a non-empty context and question.",
                "confidence": 0.0,
                "is_dummy_model": self.is_dummy,
            }

        c_tensor, q_tensor, c_mask, q_mask, context_tokens = self._preprocess(context, question)

        with torch.no_grad():
            start_logits, end_logits = self.model(
                context=c_tensor,
                query=q_tensor,
                context_mask=c_mask,
                query_mask=q_mask,
            )

        answer, confidence = self._postprocess(start_logits, end_logits, context_tokens)

        return {
            "answer": answer,
            "confidence": confidence,
            "is_dummy_model": self.is_dummy,
        }


pipeline = None


def get_inference_pipeline() -> InferencePipeline:
    global pipeline
    if pipeline is None:
        pipeline = InferencePipeline()
    return pipeline
