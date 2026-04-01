import os
import httpx
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

logger = logging.getLogger(__name__)

TMDB_BASE_URL = "https://api.themoviedb.org/3"

# logger.info("TMDB API KEY loaded: %s", TMDB_API_KEY[:10] if TMDB_API_KEY else "NOT FOUND")

async def get_movie_details(movie_id: int) -> dict | None:
    """
    Fetch movie details from TMDB API.
    Returns title, overview, poster, rating and genres.
    """

    TMDB_API_KEY = os.getenv("TMDB_API_KEY")
    
    if not TMDB_API_KEY:
        logger.error("TMDB_API_KEY not set in .env file")
        return None

    url = f"{TMDB_BASE_URL}/movie/{movie_id}"
    headers = {"Authorization": f"Bearer {TMDB_API_KEY}"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            return {
                "tmdb_id": data["id"],
                "title": data["title"],
                "overview": data.get("overview"),
                "release_date": data.get("release_date"),
                "vote_average": data.get("vote_average"),
                "poster_url": f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
                              if data.get("poster_path") else None,
                "genres": [g["name"] for g in data.get("genres", [])]
            }

        except Exception as e:
            logger.error("TMDB fetch failed for movie %d: %s", movie_id, e)
            return None


async def get_movies_details(movie_ids: list[int]) -> list[dict]:
    """
    Fetch details for multiple movies concurrently.
    """
    import asyncio
    tasks = [get_movie_details(movie_id) for movie_id in movie_ids]
    results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]