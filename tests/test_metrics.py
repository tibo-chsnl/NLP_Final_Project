"""Tests for evaluation metrics (EM & F1)."""

from src.evaluation.metrics import (
    compute_exact_match,
    compute_f1,
    compute_metrics,
    evaluate_predictions,
    normalize_answer,
)


def test_normalize_answer():
    assert normalize_answer("The Louvre Museum") == "louvre museum"
    assert normalize_answer("An apple") == "apple"


def test_exact_match_positive():
    assert compute_exact_match("Paris", "Paris") == 1
    assert compute_exact_match("paris", "Paris") == 1
    assert compute_exact_match("The Paris", "Paris") == 1


def test_exact_match_negative():
    assert compute_exact_match("London", "Paris") == 0


def test_f1_perfect():
    assert compute_f1("the capital of France", "the capital of France") == 1.0


def test_f1_partial():
    f1 = compute_f1("capital of France", "the capital of France is Paris")
    assert 0.0 < f1 < 1.0


def test_f1_no_overlap():
    assert compute_f1("hello", "world") == 0.0


def test_f1_empty():
    assert compute_f1("", "") == 1.0
    assert compute_f1("hello", "") == 0.0
    assert compute_f1("", "hello") == 0.0


def test_compute_metrics_multiple_golds():
    result = compute_metrics("Paris", ["Paris", "paris", "The Paris"])
    assert result["exact_match"] == 1
    assert result["f1"] == 1.0


def test_compute_metrics_unanswerable():
    result = compute_metrics("", [])
    assert result["exact_match"] == 1
    assert result["f1"] == 1.0


def test_evaluate_predictions():
    preds = {"q1": "Paris", "q2": "London"}
    golds = {"q1": ["Paris"], "q2": ["Berlin"]}
    result = evaluate_predictions(preds, golds)
    assert result["exact_match"] == 50.0
    assert result["total"] == 2


def test_evaluate_empty_predictions():
    result = evaluate_predictions({}, {"q1": ["Paris"]})
    assert result["total"] == 0
