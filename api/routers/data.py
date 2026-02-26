"""Data statistics and management endpoints."""

from pathlib import Path

from fastapi import APIRouter, HTTPException

from src.data.loader import load_squad

router = APIRouter(prefix="/data", tags=["Data"])

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


@router.get("/stats")
async def dataset_stats():
    """Return statistics about the loaded SQuAD datasets."""
    stats = {}

    train_path = DATA_DIR / "train-v2.0.json"
    dev_path = DATA_DIR / "dev-v2.0.json"

    if train_path.exists():
        ds = load_squad(train_path)
        stats["train"] = ds.stats()
    else:
        stats["train"] = {"error": "File not found (run `dvc pull` first)"}

    if dev_path.exists():
        ds = load_squad(dev_path)
        stats["dev"] = ds.stats()
    else:
        stats["dev"] = {"error": "File not found (run `dvc pull` first)"}

    return stats


@router.get("/sample")
async def dataset_sample(split: str = "dev", n: int = 3):
    """Return a small sample of QA examples from the dataset."""
    filepath = DATA_DIR / f"{split}-v2.0.json"
    if not filepath.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Dataset '{split}' not found. Run `dvc pull` first.",
        )

    ds = load_squad(filepath)
    examples = ds.answerable[:n]
    return [
        {
            "id": ex.id,
            "context": ex.context[:200] + "..." if len(ex.context) > 200 else ex.context,
            "question": ex.question,
            "answers": ex.answer_texts,
        }
        for ex in examples
    ]
