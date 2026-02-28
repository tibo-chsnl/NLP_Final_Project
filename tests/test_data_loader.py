"""Tests for SQuAD data loader."""

import json

import pytest

from src.data.loader import SQuADDataset, load_squad, load_squad_from_dict

SAMPLE_SQUAD = {
    "version": "v2.0-test",
    "data": [
        {
            "title": "Test Article",
            "paragraphs": [
                {
                    "context": "Paris is the capital of France.",
                    "qas": [
                        {
                            "id": "q1",
                            "question": "What is the capital of France?",
                            "answers": [{"text": "Paris", "answer_start": 0}],
                            "is_impossible": False,
                        },
                        {
                            "id": "q2",
                            "question": "What is the capital of Germany?",
                            "answers": [],
                            "is_impossible": True,
                        },
                    ],
                }
            ],
        }
    ],
}


def test_load_from_dict():
    ds = load_squad_from_dict(SAMPLE_SQUAD)
    assert isinstance(ds, SQuADDataset)
    assert len(ds) == 2
    assert ds.version == "v2.0-test"


def test_answerable_unanswerable():
    ds = load_squad_from_dict(SAMPLE_SQUAD)
    assert len(ds.answerable) == 1
    assert len(ds.unanswerable) == 1
    assert ds.answerable[0].id == "q1"
    assert ds.unanswerable[0].id == "q2"


def test_example_properties():
    ds = load_squad_from_dict(SAMPLE_SQUAD)
    ex = ds.answerable[0]
    assert ex.answer_texts == ["Paris"]
    assert ex.answer_starts == [0]
    assert ex.context == "Paris is the capital of France."


def test_stats():
    ds = load_squad_from_dict(SAMPLE_SQUAD)
    stats = ds.stats()
    assert stats["total"] == 2
    assert stats["answerable"] == 1
    assert stats["unanswerable"] == 1
    assert stats["unique_contexts"] == 1


def test_load_from_file(tmp_path):
    filepath = tmp_path / "test_squad.json"
    filepath.write_text(json.dumps(SAMPLE_SQUAD))
    ds = load_squad(filepath)
    assert len(ds) == 2


def test_load_missing_file():
    with pytest.raises(FileNotFoundError):
        load_squad("/nonexistent/file.json")


def test_load_invalid_format():
    with pytest.raises(ValueError, match="missing 'data' key"):
        load_squad_from_dict({"version": "2.0"})
