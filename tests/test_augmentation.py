"""Tests for data augmentation pipeline."""

import json

import pytest

from src.data.augmentation import (
    augment_dataset,
    augment_from_triplets,
    create_squad_entry,
)


def test_create_squad_entry():
    entry = create_squad_entry(
        context="Paris is the capital of France.",
        question="What is the capital of France?",
        answer_text="Paris",
    )
    assert entry["title"] == "User Submitted"
    assert len(entry["paragraphs"]) == 1
    qa = entry["paragraphs"][0]["qas"][0]
    assert qa["answers"][0]["text"] == "Paris"
    assert qa["answers"][0]["answer_start"] == 0


def test_create_squad_entry_auto_start():
    entry = create_squad_entry(
        context="The Eiffel Tower is in Paris.",
        question="Where is the Eiffel Tower?",
        answer_text="Paris",
    )
    assert entry["paragraphs"][0]["qas"][0]["answers"][0]["answer_start"] == 23


def test_create_squad_entry_answer_not_found():
    with pytest.raises(ValueError, match="not found in context"):
        create_squad_entry(
            context="Hello world",
            question="Where?",
            answer_text="Nowhere",
        )


def test_augment_dataset(tmp_path):
    original = {
        "version": "v2.0",
        "data": [{"title": "Original", "paragraphs": []}],
    }
    filepath = tmp_path / "squad.json"
    filepath.write_text(json.dumps(original))

    new_entry = create_squad_entry(
        context="Test context.",
        question="Test question?",
        answer_text="Test",
    )
    output = tmp_path / "augmented.json"
    augment_dataset(filepath, [new_entry], output)

    with open(output) as f:
        result = json.load(f)
    assert len(result["data"]) == 2


def test_augment_from_triplets(tmp_path):
    original = {"version": "v2.0", "data": []}
    filepath = tmp_path / "squad.json"
    filepath.write_text(json.dumps(original))

    triplets = [
        {
            "context": "Mars is a planet.",
            "question": "What is Mars?",
            "answer": "a planet",
        },
    ]
    augment_from_triplets(filepath, triplets)

    with open(filepath) as f:
        result = json.load(f)
    assert len(result["data"]) == 1
