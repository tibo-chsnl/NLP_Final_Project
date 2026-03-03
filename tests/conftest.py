from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture(autouse=True)
def mock_inference_model():
    """Globally mock the InferencePipeline model loading for tests.

    Ensures that tests don't crash with a RuntimeError when run locally
    without DVC checkpoints downloaded.
    """
    with patch("api.inference.InferencePipeline._load_model", return_value=None):
        from api.inference import get_inference_pipeline
        from model.qa_model import QAModel

        pipeline = get_inference_pipeline()
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
        yield pipeline


@pytest.fixture
def client():
    """FastAPI test client fixture."""
    return TestClient(app)
