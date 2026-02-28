"""Tests for dataset splitting."""

import pytest

from src.data.loader import QAExample, SQuADDataset
from src.data.splitter import split_dataset, split_dev_into_val_test


def _make_dataset(n_contexts: int = 10, qas_per_context: int = 3) -> SQuADDataset:
    """Create a dummy dataset with distinct contexts."""
    examples = []
    for i in range(n_contexts):
        context = f"Context number {i} with some text."
        for j in range(qas_per_context):
            examples.append(
                QAExample(
                    id=f"q_{i}_{j}",
                    context=context,
                    question=f"Question {j} about context {i}?",
                    answers=[{"text": "answer", "answer_start": 0}],
                )
            )
    return SQuADDataset(examples=examples, version="test")


def test_split_sizes():
    ds = _make_dataset(100, 2)
    train, val, test = split_dataset(ds, 0.8, 0.1, 0.1)
    assert len(train) + len(val) + len(test) == len(ds)


def test_split_no_overlap():
    ds = _make_dataset(50, 3)
    train, val, test = split_dataset(ds, 0.7, 0.15, 0.15)
    train_ids = {ex.id for ex in train.examples}
    val_ids = {ex.id for ex in val.examples}
    test_ids = {ex.id for ex in test.examples}
    assert train_ids.isdisjoint(val_ids)
    assert train_ids.isdisjoint(test_ids)
    assert val_ids.isdisjoint(test_ids)


def test_split_no_context_leakage():
    ds = _make_dataset(20, 5)
    train, val, test = split_dataset(ds, 0.6, 0.2, 0.2)
    train_ctx = {ex.context for ex in train.examples}
    val_ctx = {ex.context for ex in val.examples}
    test_ctx = {ex.context for ex in test.examples}
    assert train_ctx.isdisjoint(val_ctx)
    assert train_ctx.isdisjoint(test_ctx)
    assert val_ctx.isdisjoint(test_ctx)


def test_split_deterministic():
    ds = _make_dataset(30, 2)
    t1, v1, te1 = split_dataset(ds, 0.7, 0.15, 0.15, seed=123)
    t2, v2, te2 = split_dataset(ds, 0.7, 0.15, 0.15, seed=123)
    assert [e.id for e in t1.examples] == [e.id for e in t2.examples]
    assert [e.id for e in v1.examples] == [e.id for e in v2.examples]


def test_split_invalid_ratios():
    ds = _make_dataset(10, 1)
    with pytest.raises(ValueError, match="sum to 1.0"):
        split_dataset(ds, 0.5, 0.3, 0.3)


def test_split_dev_into_val_test():
    ds = _make_dataset(20, 2)
    val, test = split_dev_into_val_test(ds, val_ratio=0.5)
    assert len(val) + len(test) == len(ds)
    val_ctx = {ex.context for ex in val.examples}
    test_ctx = {ex.context for ex in test.examples}
    assert val_ctx.isdisjoint(test_ctx)
