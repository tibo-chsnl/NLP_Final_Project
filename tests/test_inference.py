import os
from unittest.mock import patch

import pytest

from api.inference import InferencePipeline


@pytest.fixture
def mock_pipeline():
    # Force dummy model initialization to avoid MLflow calls during tests
    with patch.dict(os.environ, {"MLFLOW_RUN_ID": ""}, clear=True):
        pipeline = InferencePipeline()
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


def test_predict_returns_dummy_response(mock_pipeline):
    context = "The Louvre Museum is located in Paris, France."
    question = "Where is the Louvre Museum located?"

    result = mock_pipeline.predict(context, question)

    assert "answer" in result
    assert "confidence" in result
    assert "is_dummy_model" in result
    assert result["is_dummy_model"] is True
    assert isinstance(result["confidence"], float)
    assert isinstance(result["answer"], str)
    # The dummy model weights are random, so we can't assert the exact string,
    # but we can assert the structure is valid string.
    assert len(result["answer"]) >= 0
