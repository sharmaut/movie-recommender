from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting ML service...")
    yield
    logger.info("Shutting down ML service.")

app = FastAPI(
    title="Movie Recommender ML Service",
    description="Collaborative Filtering recommendations for the Java backend.",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
def health_check():
    return {"status": "ok"}