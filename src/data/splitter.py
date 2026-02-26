"""Dataset splitting utilities.

Provides deterministic train/validation/test splits for SQuAD data,
splitting at the article/context level to prevent data leakage.
"""

from __future__ import annotations

import random

from src.data.loader import QAExample, SQuADDataset


def split_dataset(
    dataset: SQuADDataset,
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
    test_ratio: float = 0.1,
    seed: int = 42,
) -> tuple[SQuADDataset, SQuADDataset, SQuADDataset]:
    """Split a SQuAD dataset into train/val/test by unique contexts.

    Splitting by context (not by individual QA pairs) prevents
    questions from the same paragraph appearing in different splits,
    which would cause data leakage.

    Args:
        dataset: The full SQuADDataset to split.
        train_ratio: Fraction for training.
        val_ratio: Fraction for validation.
        test_ratio: Fraction for testing.
        seed: Random seed for reproducibility.

    Returns:
        Tuple of (train, val, test) SQuADDatasets.

    Raises:
        ValueError: If ratios don't sum to 1.0.
    """
    if abs((train_ratio + val_ratio + test_ratio) - 1.0) > 1e-6:
        raise ValueError(
            f"Ratios must sum to 1.0, got {train_ratio + val_ratio + test_ratio}"
        )

    # Group examples by context to prevent data leakage
    context_groups: dict[str, list[QAExample]] = {}
    for ex in dataset.examples:
        context_groups.setdefault(ex.context, []).append(ex)

    contexts = list(context_groups.keys())
    rng = random.Random(seed)
    rng.shuffle(contexts)

    n = len(contexts)
    train_end = int(n * train_ratio)
    val_end = train_end + int(n * val_ratio)

    train_contexts = set(contexts[:train_end])
    val_contexts = set(contexts[train_end:val_end])
    test_contexts = set(contexts[val_end:])

    train_examples = [ex for ex in dataset.examples if ex.context in train_contexts]
    val_examples = [ex for ex in dataset.examples if ex.context in val_contexts]
    test_examples = [ex for ex in dataset.examples if ex.context in test_contexts]

    return (
        SQuADDataset(examples=train_examples, version=dataset.version),
        SQuADDataset(examples=val_examples, version=dataset.version),
        SQuADDataset(examples=test_examples, version=dataset.version),
    )


def split_dev_into_val_test(
    dataset: SQuADDataset,
    val_ratio: float = 0.5,
    seed: int = 42,
) -> tuple[SQuADDataset, SQuADDataset]:
    """Split the SQuAD dev set into validation and test.

    Useful when using `train-v2.0.json` as training data and
    splitting `dev-v2.0.json` into separate val/test sets.

    Args:
        dataset: The dev SQuADDataset.
        val_ratio: Fraction for validation (rest goes to test).
        seed: Random seed.

    Returns:
        Tuple of (validation, test) SQuADDatasets.
    """
    test_ratio = 1.0 - val_ratio
    _, val, test = split_dataset(
        dataset,
        train_ratio=0.0,
        val_ratio=val_ratio,
        test_ratio=test_ratio,
        seed=seed,
    )
    return val, test
