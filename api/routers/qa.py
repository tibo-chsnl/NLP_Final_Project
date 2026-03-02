from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/qa", tags=["Question Answering"])


class QuestionRequest(BaseModel):
    context: str
    question: str


class AnswerResponse(BaseModel):
    answer: str
    confidence: float
    is_dummy: bool = False


@router.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    if not request.context or not request.question:
        raise HTTPException(status_code=400, detail="Context and question cannot be empty")

    try:
        from api.inference import get_inference_pipeline

        pipeline = get_inference_pipeline()

        # Predict uses the PyTorch model
        result = pipeline.predict(request.context, request.question)

        return AnswerResponse(
            answer=result["answer"],
            confidence=result["confidence"],
            is_dummy=result.get("is_dummy_model", False),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
