# Data Pipeline Documentation

This document describes the data processing pipeline for the Document QA Assistant project.

## Overview

The data pipeline handles loading, preprocessing, splitting, and augmenting the **SQuAD 2.0** dataset for training a Question Answering neural network.

```
data/train-v2.0.json  ──►  loader.py  ──►  preprocessing.py  ──►  Model Training
data/dev-v2.0.json    ──►  loader.py  ──►  splitter.py       ──►  Val/Test Sets
User Feedback (DB)    ──►  augmentation.py  ──►  DVC re-version
```

---

## Modules

### `src/data/loader.py` — SQuAD Parser
Loads SQuAD 2.0 JSON files into typed `QAExample` dataclasses.

```python
from src.data.loader import load_squad

dataset = load_squad("data/train-v2.0.json")
print(dataset.stats())
# {'total': 130319, 'answerable': 86821, 'unanswerable': 43498, 'unique_contexts': 18891}
```

### `src/data/preprocessing.py` — Tokenization & Vocabulary
Text cleaning, tokenization, vocabulary building, and text-to-indices conversion.

```python
from src.data.preprocessing import tokenize, build_vocabulary, text_to_indices

tokens = tokenize("The Louvre is in Paris.")
vocab = build_vocabulary(["The Louvre is in Paris.", "Paris is beautiful."])
indices = text_to_indices("The Louvre is in Paris.", vocab, max_len=10)
```

### `src/data/splitter.py` — Dataset Splitting
Splits data at the **context level** to prevent data leakage.

```python
from src.data.splitter import split_dataset, split_dev_into_val_test

train, val, test = split_dataset(dataset, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1)
# Or for the dev set specifically:
val, test = split_dev_into_val_test(dev_dataset, val_ratio=0.5)
```

### `src/evaluation/metrics.py` — EM & F1 Scores
Exact Match and F1 Score evaluation, compatible with the official SQuAD evaluation script.

```python
from src.evaluation.metrics import compute_metrics, evaluate_predictions

result = compute_metrics("Paris", ["Paris", "paris"])
# {'exact_match': 1, 'f1': 1.0}
```

### `src/data/augmentation.py` — Data Augmentation
Merges user-submitted QA triplets into the DVC-tracked training data.

```python
from src.data.augmentation import augment_from_triplets

triplets = [{"context": "...", "question": "...", "answer": "..."}]
augment_from_triplets("data/train-v2.0.json", triplets)
```

---

## DVC (Data Version Control)

### Setup
Data files are tracked by DVC with a remote on OneDrive:
```bash
uv sync --dev          # Install dependencies
uv run dvc pull        # Download data files
```

### After modifying data
```bash
uv run dvc add data/train-v2.0.json data/dev-v2.0.json
uv run dvc push
git add data/*.dvc data/.gitignore
git commit -m "data: update training data"
```

---

## Running Tests
```bash
uv run pytest tests/ -v
```
