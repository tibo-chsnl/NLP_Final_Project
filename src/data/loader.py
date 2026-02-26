"""SQuAD 2.0 dataset loader and parser.

Loads JSON files in the SQuAD 2.0 format and extracts structured
(context, question, answer) triplets for training and evaluation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class QAExample:
    """A single QA example from SQuAD."""

    id: str
    context: str
    question: str
    answers: list[dict[str, str | int]]
    is_impossible: bool = False

    @property
    def answer_texts(self) -> list[str]:
        return [a["text"] for a in self.answers]

    @property
    def answer_starts(self) -> list[int]:
        return [a["answer_start"] for a in self.answers]


@dataclass
class SQuADDataset:
    """Parsed SQuAD dataset."""

    examples: list[QAExample] = field(default_factory=list)
    version: str = ""

    @property
    def answerable(self) -> list[QAExample]:
        return [ex for ex in self.examples if not ex.is_impossible]

    @property
    def unanswerable(self) -> list[QAExample]:
        return [ex for ex in self.examples if ex.is_impossible]

    def __len__(self) -> int:
        return len(self.examples)

    def stats(self) -> dict:
        return {
            "total": len(self.examples),
            "answerable": len(self.answerable),
            "unanswerable": len(self.unanswerable),
            "unique_contexts": len({ex.context for ex in self.examples}),
        }


def load_squad(filepath: str | Path) -> SQuADDataset:
    """Load and parse a SQuAD 2.0 JSON file.

    Args:
        filepath: Path to the SQuAD JSON file.

    Returns:
        A SQuADDataset containing all parsed QA examples.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the JSON structure is invalid.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"SQuAD file not found: {filepath}")

    with open(filepath, encoding="utf-8") as f:
        raw = json.load(f)

    if "data" not in raw:
        raise ValueError("Invalid SQuAD format: missing 'data' key")

    version = raw.get("version", "unknown")
    examples = []

    for article in raw["data"]:
        for paragraph in article["paragraphs"]:
            context = paragraph["context"]
            for qa in paragraph["qas"]:
                examples.append(
                    QAExample(
                        id=qa["id"],
                        context=context,
                        question=qa["question"],
                        answers=qa.get("answers", []),
                        is_impossible=qa.get("is_impossible", False),
                    )
                )

    return SQuADDataset(examples=examples, version=version)


def load_squad_from_dict(data: dict) -> SQuADDataset:
    """Load SQuAD data from an already-parsed dictionary.

    Useful for testing or loading from APIs.
    """
    if "data" not in data:
        raise ValueError("Invalid SQuAD format: missing 'data' key")

    examples = []
    for article in data["data"]:
        for paragraph in article["paragraphs"]:
            context = paragraph["context"]
            for qa in paragraph["qas"]:
                examples.append(
                    QAExample(
                        id=qa["id"],
                        context=context,
                        question=qa["question"],
                        answers=qa.get("answers", []),
                        is_impossible=qa.get("is_impossible", False),
                    )
                )

    return SQuADDataset(examples=examples, version=data.get("version", "unknown"))
