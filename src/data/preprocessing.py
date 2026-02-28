"""Text preprocessing and tokenization for QA tasks.

Provides cleaning, tokenization, and vocabulary-building functions
for preparing SQuAD data for the neural network.
"""

from __future__ import annotations

import re
import string
from collections import Counter


def clean_text(text: str) -> str:
    """Clean raw text: normalize whitespace and unicode.

    Args:
        text: Raw input text.

    Returns:
        Cleaned text string.
    """
    text = text.replace("\u00a0", " ")  # non-breaking space
    text = text.replace("\u200b", "")  # zero-width space
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenize(text: str, lowercase: bool = True) -> list[str]:
    """Simple whitespace + punctuation tokenizer.

    Args:
        text: Input text.
        lowercase: Whether to lowercase tokens.

    Returns:
        List of tokens.
    """
    if lowercase:
        text = text.lower()
    tokens = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)
    return tokens


def normalize_answer(text: str) -> str:
    """Normalize answer text for evaluation (matching SQuAD eval script).

    Lowercases, removes punctuation, articles, and extra whitespace.
    """

    def remove_articles(t: str) -> str:
        return re.sub(r"\b(a|an|the)\b", " ", t, flags=re.UNICODE)

    def remove_punc(t: str) -> str:
        return "".join(ch for ch in t if ch not in string.punctuation)

    def white_space_fix(t: str) -> str:
        return " ".join(t.split())

    return white_space_fix(remove_articles(remove_punc(text.lower())))


def build_vocabulary(
    texts: list[str], min_freq: int = 1, max_size: int | None = None
) -> dict[str, int]:
    """Build a word-to-index vocabulary from a list of texts.

    Args:
        texts: List of raw text strings.
        min_freq: Minimum word frequency to include.
        max_size: Maximum vocabulary size (None = unlimited).

    Returns:
        Dictionary mapping word → index.
    """
    counter: Counter[str] = Counter()
    for text in texts:
        counter.update(tokenize(text))

    # Special tokens
    vocab = {"<PAD>": 0, "<UNK>": 1}
    idx = 2

    most_common = counter.most_common(max_size)
    for word, freq in most_common:
        if freq >= min_freq and word not in vocab:
            vocab[word] = idx
            idx += 1

    return vocab


def text_to_indices(text: str, vocab: dict[str, int], max_len: int | None = None) -> list[int]:
    """Convert text to a list of vocabulary indices.

    Args:
        text: Input text.
        vocab: Word-to-index mapping.
        max_len: Optional max length (truncate or pad).

    Returns:
        List of integer indices.
    """
    tokens = tokenize(text)
    unk_idx = vocab.get("<UNK>", 1)
    indices = [vocab.get(tok, unk_idx) for tok in tokens]

    if max_len is not None:
        pad_idx = vocab.get("<PAD>", 0)
        if len(indices) > max_len:
            indices = indices[:max_len]
        else:
            indices.extend([pad_idx] * (max_len - len(indices)))

    return indices
