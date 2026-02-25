from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class PredictRequest(BaseModel):
    context: str
    question: str


class PredictResponse(BaseModel):
    text: str
    start: int
    end: int
    confidence: float


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    sentences = [s.strip() for s in req.context.split(".") if s.strip()]
    best = sentences[0] if sentences else req.context
    start = req.context.find(best)
    return PredictResponse(
        text=best,
        start=start,
        end=start + len(best),
        confidence=0.85,
    )
