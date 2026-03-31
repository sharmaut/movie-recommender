from pydantic import BaseModel, Field
from typing import Optional

class RecommendationRequest(BaseModel):
    user_id: int = Field(alias="userId")
    watched_movie_ids: list[int] = Field(alias="watchedMovieIds")
    limit: int = 10

    model_config = {"populate_by_name": True}

class RecommendationResponse(BaseModel):
    user_id: int
    recommended_movie_ids: list[int]
    model_version: str = "1.0.0"
    confidence_scores: Optional[list[float]] = None

