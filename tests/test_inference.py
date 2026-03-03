from unittest.mock import patch

import pytest

from api.inference import InferencePipeline


@pytest.fixture
def mock_pipeline():
    with patch("api.inference.InferencePipeline._load_model", return_value=None):
        pipeline = InferencePipeline()
        # Initialize a basic dummy model so the pipeline works
        from model.qa_model import QAModel

        pipeline.vocab = {"<PAD>": 0, "<UNK>": 1}
        pipeline.vocab_size = 10000
        pipeline.model = QAModel(
            vocab_size=pipeline.vocab_size,
            embedding_dim=64,
            hidden_dim=64,
            dropout=0.0,
        )
        pipeline.model.to(pipeline.device)
        pipeline.model.eval()
        pipeline.is_dummy = True
    return pipeline


def test_inference_pipeline_initialization(mock_pipeline):
    assert mock_pipeline is not None
    assert mock_pipeline.model is not None
    assert mock_pipeline.is_dummy is True
    # Model should have valid vocab and device
    assert mock_pipeline.vocab_size > 0


def test_preprocessing(mock_pipeline):
    context = "The quick brown fox jumps over the lazy dog."
    question = "Who jumps over the dog?"

    c_tensor, q_tensor, c_mask, q_mask, tokens = mock_pipeline._preprocess(context, question)

    assert c_tensor.dim() == 2
    assert q_tensor.dim() == 2
    assert c_mask.shape == c_tensor.shape
    assert q_mask.shape == q_tensor.shape
    assert len(tokens) > 0
    assert isinstance(tokens, list)


def test_predict_returns_valid_response(mock_pipeline):
    context = "The Louvre Museum is located in Paris, France."
    question = "Where is the Louvre Museum located?"

    result = mock_pipeline.predict(context, question)

    assert "answer" in result
    assert "confidence" in result
    assert "is_dummy_model" in result
    assert result["is_dummy_model"] is True
    assert isinstance(result["confidence"], float)
    assert isinstance(result["answer"], str)
    assert len(result["answer"]) >= 0
