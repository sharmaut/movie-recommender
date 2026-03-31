from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import logging

from models import RecommendationRequest, RecommendationResponse
from recommender import CollaborativeFilter

from database import get_viewing_history

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cf_model = CollaborativeFilter()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting ML service...")
    data = get_viewing_history()
    if data:
        cf_model.fit(data)
        logger.info("Model trained successfully")
    else:
        logger.warning("No training data found - model not trained")
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
    return {"status": "ok",
            "model_trained": cf_model.user_item_matrix is not None
        }

@app.post("/recommendations", response_model=RecommendationResponse)
def get_recommendations(request: RecommendationRequest):
    if cf_model.user_item_matrix is None:
        raise HTTPException(
            status_code=503,
            detail="Model not trained yet. No viewing history available."
        )
    
    recommended_ids, scores = cf_model.recommend(
        user_id=request.user_id,
        watched_ids=request.watched_movie_ids,
        limit=request.limit
    )

    return RecommendationResponse(
        user_id=request.user_id,
        recommended_movie_ids=recommended_ids,
        confidence_scores=scores
    )