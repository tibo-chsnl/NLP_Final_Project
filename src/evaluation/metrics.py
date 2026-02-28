"""Evaluation metrics for QA: Exact Match (EM) and F1 Score.

Extracted and refactored from the official SQuAD 2.0 evaluation script
into clean, reusable functions for use during training and evaluation.
"""

from __future__ import annotations

import collections
import re
import string


def normalize_answer(text: str) -> str:
    """Normalize text for evaluation comparison.

    Applies: lowercase → remove punctuation → remove articles → fix whitespace.
    """

    def remove_articles(t: str) -> str:
        return re.sub(r"\b(a|an|the)\b", " ", t, flags=re.UNICODE)

    def remove_punc(t: str) -> str:
        return "".join(ch for ch in t if ch not in string.punctuation)

    def white_space_fix(t: str) -> str:
        return " ".join(t.split())

    return white_space_fix(remove_articles(remove_punc(text.lower())))


def compute_exact_match(prediction: str, ground_truth: str) -> int:
    """Compute Exact Match score between prediction and ground truth.

    Args:
        prediction: The model's predicted answer.
        ground_truth: The gold answer.

    Returns:
        1 if normalized texts match exactly, 0 otherwise.
    """
    return int(normalize_answer(prediction) == normalize_answer(ground_truth))


def compute_f1(prediction: str, ground_truth: str) -> float:
    """Compute token-level F1 score between prediction and ground truth.

    Args:
        prediction: The model's predicted answer.
        ground_truth: The gold answer.

    Returns:
        F1 score between 0.0 and 1.0.
    """
    pred_tokens = normalize_answer(prediction).split()
    gold_tokens = normalize_answer(ground_truth).split()

    if not gold_tokens and not pred_tokens:
        return 1.0
    if not gold_tokens or not pred_tokens:
        return 0.0

    common = collections.Counter(pred_tokens) & collections.Counter(gold_tokens)
    num_same = sum(common.values())

    if num_same == 0:
        return 0.0

    precision = num_same / len(pred_tokens)
    recall = num_same / len(gold_tokens)
    return (2 * precision * recall) / (precision + recall)


def compute_metrics(prediction: str, ground_truths: list[str]) -> dict[str, float]:
    """Compute both EM and F1 against multiple gold answers.

    Takes the max score over all gold answers (standard SQuAD practice).

    Args:
        prediction: The model's predicted answer.
        ground_truths: List of acceptable gold answers.

    Returns:
        Dict with 'exact_match' and 'f1' scores.
    """
    if not ground_truths:
        # Unanswerable question: correct if prediction is empty
        em = int(normalize_answer(prediction) == "")
        f1 = float(em)
        return {"exact_match": em, "f1": f1}

    em = max(compute_exact_match(prediction, gt) for gt in ground_truths)
    f1 = max(compute_f1(prediction, gt) for gt in ground_truths)
    return {"exact_match": em, "f1": f1}


def evaluate_predictions(
    predictions: dict[str, str],
    ground_truths: dict[str, list[str]],
) -> dict[str, float]:
    """Evaluate a full set of predictions against ground truths.

    Args:
        predictions: Dict mapping question_id → predicted answer.
        ground_truths: Dict mapping question_id → list of gold answers.

    Returns:
        Dict with average 'exact_match' and 'f1' scores.
    """
    if not predictions:
        return {"exact_match": 0.0, "f1": 0.0, "total": 0}

    total_em = 0.0
    total_f1 = 0.0
    count = 0

    for qid, pred in predictions.items():
        if qid not in ground_truths:
            continue
        metrics = compute_metrics(pred, ground_truths[qid])
        total_em += metrics["exact_match"]
        total_f1 += metrics["f1"]
        count += 1

    if count == 0:
        return {"exact_match": 0.0, "f1": 0.0, "total": 0}

    return {
        "exact_match": 100.0 * total_em / count,
        "f1": 100.0 * total_f1 / count,
        "total": count,
    }
