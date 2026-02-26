"""Tests for text preprocessing and tokenization."""

from src.data.preprocessing import (
    clean_text,
    tokenize,
    normalize_answer,
    build_vocabulary,
    text_to_indices,
)


def test_clean_text_whitespace():
    assert clean_text("  hello   world  ") == "hello world"


def test_clean_text_special_chars():
    assert clean_text("hello\u00a0world\u200b") == "hello world"


def test_tokenize_basic():
    tokens = tokenize("Hello, world!")
    assert tokens == ["hello", ",", "world", "!"]


def test_tokenize_no_lowercase():
    tokens = tokenize("Hello World", lowercase=False)
    assert tokens == ["Hello", "World"]


def test_normalize_answer():
    assert normalize_answer("The Louvre Museum") == "louvre museum"
    assert normalize_answer("  a  cat  ") == "cat"


def test_normalize_answer_punctuation():
    assert normalize_answer("hello, world!") == "hello world"


def test_build_vocabulary():
    texts = ["hello world", "hello there"]
    vocab = build_vocabulary(texts)
    assert "<PAD>" in vocab
    assert "<UNK>" in vocab
    assert "hello" in vocab
    assert vocab["<PAD>"] == 0
    assert vocab["<UNK>"] == 1


def test_build_vocabulary_min_freq():
    texts = ["hello world", "hello there"]
    vocab = build_vocabulary(texts, min_freq=2)
    assert "hello" in vocab
    assert "world" not in vocab


def test_build_vocabulary_max_size():
    texts = ["a b c d e f"]
    vocab = build_vocabulary(texts, max_size=3)
    # PAD, UNK + 3 words = 5 total
    assert len(vocab) == 5


def test_text_to_indices():
    vocab = {"<PAD>": 0, "<UNK>": 1, "hello": 2, "world": 3}
    indices = text_to_indices("hello world", vocab)
    assert indices == [2, 3]


def test_text_to_indices_padding():
    vocab = {"<PAD>": 0, "<UNK>": 1, "hello": 2}
    indices = text_to_indices("hello", vocab, max_len=3)
    assert indices == [2, 0, 0]


def test_text_to_indices_truncation():
    vocab = {"<PAD>": 0, "<UNK>": 1, "a": 2, "b": 3, "c": 4}
    indices = text_to_indices("a b c", vocab, max_len=2)
    assert indices == [2, 3]


def test_text_to_indices_unknown():
    vocab = {"<PAD>": 0, "<UNK>": 1, "hello": 2}
    indices = text_to_indices("hello unknown", vocab)
    assert indices == [2, 1]
