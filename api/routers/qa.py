from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(
    prefix="/qa",
    tags=["Question Answering"]
)

class QuestionRequest(BaseModel):
    context: str
    question: str

class AnswerResponse(BaseModel):
    answer: str
    confidence: float

@router.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    # TODO: Connect to the NLP model to get the answer
    # For now, return a mock response
    try:
        if not request.context or not request.question:
            raise HTTPException(status_code=400, detail="Context and question cannot be empty")
            
        mock_answer = "This is a placeholder answer."
        return AnswerResponse(answer=mock_answer, confidence=0.95)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
