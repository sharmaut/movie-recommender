from pydantic import BaseModel
from typing import Optional

class RecommendationRequest(BaseModel):
    user_id: int
    watched_movie_ids: list[int]
    limit: int = 10

class RecommendationResponse(BaseModel):
    user_id: int
    recommended_movie_ids: list[int]
    model_version: str = "1.0.0"
    confidence_scores: Optional[list[float]] = None

