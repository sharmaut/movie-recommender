from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from vector_search import upsert_movies, search_similar
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
    limit: int = 5,
    year_from: int = None,
    year_to: int = None
):
    api_key = os.getenv("TMDB_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}"}

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
        "vote_count.gte": 200,
        "with_original_language": language,
        "page": 1
    }

    if genre and genre.lower() in genre_map:
        params["with_genres"] = genre_map[genre.lower()]

    if year_from:
        params["primary_release_date.gte"] = f"{year_from}-01-01"
    if year_to:
        params["primary_release_date.lte"] = f"{year_to}-12-31"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.themoviedb.org/3/discover/movie",
            headers=headers,
            params=params
        )
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
        search_response = await client.get(
            "https://api.themoviedb.org/3/search/movie",
            headers=headers,
            params={"query": movie_name, "language": "en-US", "page": 1}
        )
        search_data = search_response.json()

        if not search_data.get("results"):
            raise HTTPException(status_code=404, detail="Movie not found")

        movie_id = search_data["results"][0]["id"]
        movie_title = search_data["results"][0]["title"]

        similar_response = await client.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations",
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

@app.post("/vector/populate")
async def populate_vector_db(language: str = "en"):
    api_key = os.getenv("TMDB_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}"}

    all_movies = []
    seen_ids = set()
    genre_ids = [28, 35, 18, 27, 10749, 878, 53, 16, 10751, 36]

    async with httpx.AsyncClient() as client:
        for genre_id in genre_ids:
            for page in range(1, 4):
                response = await client.get(
                    "https://api.themoviedb.org/3/discover/movie",
                    headers=headers,
                    params={
                        "sort_by": "popularity.desc",
                        "vote_count.gte": 200,
                        "with_original_language": language,
                        "with_genres": genre_id,
                        "page": page
                    }
                )
                data = response.json()
                for movie in data.get("results", []):
                    if movie["id"] not in seen_ids:
                        seen_ids.add(movie["id"])
                        all_movies.append({
                            "tmdb_id": movie["id"],
                            "title": movie["title"],
                            "overview": movie.get("overview", ""),
                            "release_date": movie.get("release_date", ""),
                            "vote_average": movie.get("vote_average", 0.0),
                            "poster_url": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"
                                         if movie.get("poster_path") else None,
                            "genres": movie.get("genre_ids", [])
                        })

    upsert_movies(all_movies)
    return {"message": f"Stored {len(all_movies)} movies in Pinecone"}

@app.get("/vector/search")
async def vector_search(query: str, limit: int = 10):
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    movies = search_similar(query, limit)

    if not movies:
        raise HTTPException(
            status_code=404,
            detail="No movies found. Try populating the vector database first."
        )

    return {
        "query": query,
        "movies": movies
    }

@app.get("/recommendations/smart")
async def smart_search(query: str, limit: int = 10):
    """
    Natural language movie search powered by Claude.
    Claude interprets the query and calls the right endpoints automatically.
    """
    import anthropic

    api_key = os.getenv("ANTHROPIC_API_KEY")
    client = anthropic.Anthropic(api_key=api_key)

    # Ask Claude to interpret the query and extract parameters
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": f"""You are a movie search assistant. A user has typed this search query: "{query}"

Analyze this query and respond with ONLY a JSON object (no explanation, no markdown) with these fields:
{{
    "search_type": "similar" or "filter" or "vector",
    "movie_name": "movie name if they mentioned a specific movie, otherwise null",
    "genre": "action/comedy/drama/horror/romance/scifi/thriller or null",
    "language": "en/hi/de/fr/es/ja/ko or null, default en",
    "mood": "a short description of the vibe they want",
    "year_from": null or a year number,
    "year_to": null or a year number
}}

Rules:
- If they mention a specific movie title, use search_type "similar"
- If they mention a genre and/or language clearly, use search_type "filter"
- If they describe a mood, vibe or theme without a specific movie, use search_type "vector"
- Only include year range if they explicitly mention a decade or time period"""
            }
        ]
    )

    # Parse Claude's response
    import json
    response_text = message.content[0].text.strip()

    try:
        params = json.loads(response_text)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Claude returned invalid JSON")

    search_type = params.get("search_type", "vector")
    movies = []
    search_description = ""

    if search_type == "similar" and params.get("movie_name"):
        # Call existing similar movies logic
        tmdb_api_key = os.getenv("TMDB_API_KEY")
        headers = {"Authorization": f"Bearer {tmdb_api_key}"}
        async with httpx.AsyncClient() as client_http:
            search_response = await client_http.get(
                "https://api.themoviedb.org/3/search/movie",
                headers=headers,
                params={"query": params["movie_name"], "language": "en-US", "page": 1}
            )
            search_data = search_response.json()
            if search_data.get("results"):
                movie_id = search_data["results"][0]["id"]
                movie_title = search_data["results"][0]["title"]
                similar_response = await client_http.get(
                    f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations",
                    headers=headers,
                    params={"language": "en-US", "page": 1}
                )
                similar_data = similar_response.json()
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
                search_description = f'Movies similar to "{movie_title}"'

    elif search_type == "filter":
        tmdb_api_key = os.getenv("TMDB_API_KEY")
        headers = {"Authorization": f"Bearer {tmdb_api_key}"}
        genre_map = {
            "action": 28, "comedy": 35, "drama": 18,
            "horror": 27, "romance": 10749, "scifi": 878, "thriller": 53
        }
        filter_params = {
            "sort_by": "vote_average.desc",
            "vote_count.gte": 200,
            "with_original_language": params.get("language", "en"),
            "page": 1
        }
        if params.get("genre") and params["genre"].lower() in genre_map:
            filter_params["with_genres"] = genre_map[params["genre"].lower()]
        if params.get("year_from"):
            filter_params["primary_release_date.gte"] = f"{params['year_from']}-01-01"
        if params.get("year_to"):
            filter_params["primary_release_date.lte"] = f"{params['year_to']}-12-31"

        async with httpx.AsyncClient() as client_http:
            response = await client_http.get(
                "https://api.themoviedb.org/3/discover/movie",
                headers=headers,
                params=filter_params
            )
            data = response.json()
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
        search_description = f'Top {params.get("genre", "")} movies'

    else:
        movies = search_similar(params.get("mood", query), limit)
        search_description = f'Movies matching "{query}"'

    return {
        "query": query,
        "interpreted_as": params,
        "search_description": search_description,
        "movies": movies
    }