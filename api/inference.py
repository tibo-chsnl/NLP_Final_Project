import os
import torch
import mlflow.pytorch
from pydantic import BaseModel
from typing import Tuple, Dict, Any

from model.qa_model import QAModel
from src.data.preprocessing import tokenize, text_to_indices

class InferencePipeline:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.vocab: Dict[str, int] = {}
        self.vocab_size = 10000 # Default fallback
        self.model = None
        self.is_dummy = True
        
        self._load_model()

    def _load_model(self):
        """
        Attempts to load the model from MLflow if MLFLOW_RUN_ID is set.
        Otherwise, initializes a dummy QAModel with random weights.
        """
        run_id = os.environ.get("MLFLOW_RUN_ID")
        
        if run_id:
            try:
                print(f"Loading model from MLflow Run ID: {run_id}")
                model_uri = f"runs:/{run_id}/model"
                self.model = mlflow.pytorch.load_model(model_uri)
                self.model.to(self.device)
                self.model.eval()
                self.is_dummy = False
                # TODO: Retrieve real vocabulary from MLflow artifacts if possible
                print("Successfully loaded model from MLflow.")
                return
            except Exception as e:
                print(f"Failed to load model from MLflow: {e}. Falling back to dummy model.")
                
        print("Initializing dummy QAModel with random weights for testing.")
        # Minimal dummy configuration
        self.vocab = {"<PAD>": 0, "<UNK>": 1}
        self.vocab_size = 10000
        self.model = QAModel(
            vocab_size=self.vocab_size,
            embedding_dim=64,
            hidden_dim=64,
            dropout=0.0
        )
        self.model.to(self.device)
        self.model.eval()
        self.is_dummy = True

    def _preprocess(self, context: str, question: str) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, list]:
        """
        Tokenizes and converts context and question into tensors.
        Returns:
            context_tensor, question_tensor, context_mask, question_mask, context_tokens
        """
        # 1. Tokenize (reusing Thibault's preprocessing)
        context_tokens = tokenize(context)
        question_tokens = tokenize(question)
        
        # 2. Convert to indices
        c_indices = [self.vocab.get(tok, self.vocab.get("<UNK>", 1)) for tok in context_tokens]
        q_indices = [self.vocab.get(tok, self.vocab.get("<UNK>", 1)) for tok in question_tokens]
        
        # 3. Create tensors and masks
        # Add batch dimension (unsqueeze(0))
        c_tensor = torch.tensor(c_indices, dtype=torch.long, device=self.device).unsqueeze(0)
        q_tensor = torch.tensor(q_indices, dtype=torch.long, device=self.device).unsqueeze(0)
        
        c_mask = torch.ones_like(c_tensor, dtype=torch.bool, device=self.device)
        q_mask = torch.ones_like(q_tensor, dtype=torch.bool, device=self.device)
        
        return c_tensor, q_tensor, c_mask, q_mask, context_tokens

    def _postprocess(self, start_logits: torch.Tensor, end_logits: torch.Tensor, context_tokens: list) -> Tuple[str, float]:
        """
        Decodes the logits into a string answer and calculates pseudo-confidence.
        """
        # Ensure we only look at valid token indices (remove batch dim)
        start_logits = start_logits.squeeze(0)
        end_logits = end_logits.squeeze(0)
        
        max_len = len(context_tokens)
        
        # Prevent selecting indices outside of context length (if model outputs padding predictions)
        start_logits = start_logits[:max_len]
        end_logits = end_logits[:max_len]

        # Simple argmax for now (could be improved with beam search or limiting end >= start)
        start_idx = torch.argmax(start_logits).item()
        
        # Mask out end indices before start index to avoid negative length answers
        mask = torch.ones_like(end_logits) * -1e9
        mask[start_idx:] = 0
        valid_end_logits = end_logits + mask
        
        end_idx = torch.argmax(valid_end_logits).item()
        
        # Decode tokens back to string
        # Note: A real system might need offset mapping to map back exactly to the original string.
        # Joining tokens with spaces is an approximation.
        answer_tokens = context_tokens[start_idx:end_idx + 1]
        answer = " ".join(answer_tokens)
        
        # Pseudo-confidence (average probability)
        start_prob = torch.softmax(start_logits, dim=0)[start_idx].item()
        end_prob = torch.softmax(valid_end_logits, dim=0)[end_idx].item()
        confidence = (start_prob + end_prob) / 2.0
        
        # Handle empty or invalid bounds
        if not answer.strip() or start_idx > end_idx:
            answer = "Unable to find a conclusive answer."
            confidence = 0.0
            
        return answer, confidence

    def predict(self, context: str, question: str) -> Dict[str, Any]:
        """
        Full inference pipeline: preprocess -> forward -> postprocess.
        """
        if not self.model:
            raise RuntimeError("Model is not initialized.")
            
        c_tensor, q_tensor, c_mask, q_mask, context_tokens = self._preprocess(context, question)
        
        with torch.no_grad():
            start_logits, end_logits = self.model(
                context=c_tensor, 
                query=q_tensor, 
                context_mask=c_mask, 
                query_mask=q_mask
            )
            
        answer, confidence = self._postprocess(start_logits, end_logits, context_tokens)
        
        return {
            "answer": answer,
            "confidence": confidence,
            "is_dummy_model": self.is_dummy
        }

# Global singleton instance for the FastAPI app
pipeline = None

def get_inference_pipeline() -> InferencePipeline:
    global pipeline
    if pipeline is None:
        pipeline = InferencePipeline()
    return pipeline
