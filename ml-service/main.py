from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import logging
import os
import httpx

load_dotenv()

from models import RecommendationRequest, RecommendationResponse, MovieRecommendationResponse
from recommender import CollaborativeFilter
from database import get_viewing_history
from tmdb import get_movies_details

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
    return {
        "status": "ok",
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

@app.post("/recommendations/detailed")
async def get_detailed_recommendations(request: RecommendationRequest):
    if cf_model.user_item_matrix is None:
        raise HTTPException(
            status_code=503,
            detail="Model not trained yet."
        )

    recommended_ids, scores = cf_model.recommend(
        user_id=request.user_id,
        watched_ids=request.watched_movie_ids,
        limit=request.limit
    )

    movies = await get_movies_details(recommended_ids)

    return {
        "user_id": request.user_id,
        "recommendations": movies,
        "model_version": "1.0.0"
    }

@app.get("/recommendations/filter")
async def filter_recommendations(
    genre: str = None,
    language: str = "en",
    limit: int = 5
):
    api_key = os.getenv("TMDB_API_KEY")
    url = "https://api.themoviedb.org/3/discover/movie"

    genre_map = {
        "action": 28,
        "comedy": 35,
        "drama": 18,
        "horror": 27,
        "romance": 10749,
        "scifi": 878,
        "thriller": 53
    }

    params = {
        "sort_by": "vote_average.desc",
        "vote_count.gte": 1000,
        "with_original_language": language,
        "page": 1
    }

    if genre and genre.lower() in genre_map:
        params["with_genres"] = genre_map[genre.lower()]

    headers = {"Authorization": f"Bearer {api_key}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        data = response.json()

    movies = []
    for movie in data.get("results", [])[:limit]:
        movies.append({
            "tmdb_id": movie["id"],
            "title": movie["title"],
            "overview": movie.get("overview"),
            "release_date": movie.get("release_date"),
            "vote_average": movie.get("vote_average"),
            "poster_url": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"
                         if movie.get("poster_path") else None,
            "genres": movie.get("genre_ids", [])
        })

    return {
        "language": language,
        "genre": genre,
        "movies": movies
    }

@app.get("/recommendations/similar")
async def similar_movies(movie_name: str, limit: int = 10):
    api_key = os.getenv("TMDB_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}"}

    async with httpx.AsyncClient() as client:
        # Step 1, search for the movie to get its ID
        search_response = await client.get(
            "https://api.themoviedb.org/3/search/movie",
            headers=headers,
            params={"query": movie_name, "language": "en-US", "page": 1}
        )
        search_data = search_response.json()

        if not search_data.get("results"):
            raise HTTPException(status_code=404, detail="Movie not found")

        # Step 2, get the first result's ID
        movie_id = search_data["results"][0]["id"]
        movie_title = search_data["results"][0]["title"]

        # Step 3, fetch similar movies
        similar_response = await client.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}/similar",
            headers=headers,
            params={"language": "en-US", "page": 1}
        )
        similar_data = similar_response.json()

    movies = []
    for movie in similar_data.get("results", [])[:limit]:
        movies.append({
            "tmdb_id": movie["id"],
            "title": movie["title"],
            "overview": movie.get("overview"),
            "release_date": movie.get("release_date"),
            "vote_average": movie.get("vote_average"),
            "poster_url": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"
                         if movie.get("poster_path") else None,
            "genres": movie.get("genre_ids", [])
        })

    return {
        "searched_movie": movie_title,
        "similar_movies": movies
    }