"""Data augmentation pipeline for SQuAD-format QA data.

Handles merging user-submitted QA triplets from the frontend/database
into the DVC-tracked training dataset.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path


def create_squad_entry(
    context: str,
    question: str,
    answer_text: str,
    answer_start: int | None = None,
    title: str = "User Submitted",
) -> dict:
    """Create a single SQuAD-format entry from a user QA triplet.

    If answer_start is not provided, it is automatically detected
    from the context string.

    Args:
        context: The paragraph text.
        question: The user's question.
        answer_text: The answer extracted from context.
        answer_start: Character offset of the answer in context.
        title: Article title (default: "User Submitted").

    Returns:
        A SQuAD-format article dictionary.

    Raises:
        ValueError: If the answer is not found in the context.
    """
    if answer_start is None:
        answer_start = context.find(answer_text)
        if answer_start == -1:
            raise ValueError(f"Answer '{answer_text}' not found in context")

    return {
        "title": title,
        "paragraphs": [
            {
                "context": context,
                "qas": [
                    {
                        "id": str(uuid.uuid4()),
                        "question": question,
                        "answers": [
                            {"text": answer_text, "answer_start": answer_start}
                        ],
                        "is_impossible": False,
                    }
                ],
            }
        ],
    }


def augment_dataset(
    original_path: str | Path,
    new_entries: list[dict],
    output_path: str | Path | None = None,
) -> Path:
    """Append new SQuAD-format entries to an existing dataset file.

    Args:
        original_path: Path to the original SQuAD JSON file.
        new_entries: List of SQuAD article dicts (from create_squad_entry).
        output_path: Where to save the augmented file.
                     If None, overwrites the original.

    Returns:
        Path to the saved augmented file.
    """
    original_path = Path(original_path)
    output_path = Path(output_path) if output_path else original_path

    with open(original_path, encoding="utf-8") as f:
        dataset = json.load(f)

    dataset["data"].extend(new_entries)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    return output_path


def augment_from_triplets(
    original_path: str | Path,
    triplets: list[dict[str, str]],
    output_path: str | Path | None = None,
) -> Path:
    """Convenience: augment dataset from a list of (context, question, answer) dicts.

    Args:
        original_path: Path to the existing SQuAD JSON.
        triplets: List of dicts with keys 'context', 'question', 'answer'.
        output_path: Output path (None = overwrite original).

    Returns:
        Path to the saved file.
    """
    entries = []
    for triplet in triplets:
        entry = create_squad_entry(
            context=triplet["context"],
            question=triplet["question"],
            answer_text=triplet["answer"],
        )
        entries.append(entry)

    return augment_dataset(original_path, entries, output_path)
