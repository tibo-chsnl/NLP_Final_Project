from fastapi import FastAPI

from api.routers import data, health, qa

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load model on startup
    from api.inference import get_inference_pipeline
    print("Initializing inference pipeline...")
    get_inference_pipeline()
    yield
    # Cleanup on shutdown (if needed)
    print("Shutting down inference pipeline...")

app = FastAPI(
    title="Document QA Assistant API",
    description="Backend API for the NLP & MLOps Final Project",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(health.router)
app.include_router(qa.router, prefix="/api/v1")
app.include_router(data.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Welcome to the Document QA Assistant API"}
