from fastapi import APIRouter

from api.config import ENVIRONMENT

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/")
async def health_check():
    from api.inference import get_inference_pipeline

    pipeline = get_inference_pipeline()
    return {
        "status": "ok",
        "environment": ENVIRONMENT,
        "model_loaded": not pipeline.is_dummy,
    }
