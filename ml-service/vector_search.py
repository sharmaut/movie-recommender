import os
import logging
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / ".env")

logger = logging.getLogger(__name__)

# Load the embedding model once at module level
# This model converts text into 384-dimensional vectors
model = SentenceTransformer("all-MiniLM-L6-v2")

def get_pinecone_index():
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX", "movie-recommender")
    pc = Pinecone(api_key=api_key)
    return pc.Index(index_name)

def upsert_movies(movies: list[dict]):
    """
    Store movies in Pinecone as vectors.
    Each movie's title + overview gets converted to a 384-dim embedding.
    Call this once to populate the index with movie data.
    """
    index = get_pinecone_index()
    vectors = []

    for movie in movies:
        # Combine title and overview to create a rich text representation
        text = f"{movie['title']}. {movie.get('overview', '')}"
        embedding = model.encode(text).tolist()

        vectors.append({
            "id": str(movie["tmdb_id"]),
            "values": embedding,
            "metadata": {
                "title": movie["title"],
                "overview": movie.get("overview", ""),
                "release_date": movie.get("release_date", ""),
                "vote_average": movie.get("vote_average", 0.0),
                "poster_url": movie.get("poster_url", ""),
                "genres": str(movie.get("genres", []))
            }
        })

    # Upsert in batches of 100
    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        index.upsert(vectors=batch)
        logger.info("Upserted batch %d of %d", i // batch_size + 1, len(vectors) // batch_size + 1)

    logger.info("Successfully stored %d movies in Pinecone", len(vectors))

def search_similar(query: str, limit: int = 10) -> list[dict]:
    """
    Search for movies similar to the query text.
    Converts the query into an embedding and finds nearest neighbours in Pinecone.
    """
    index = get_pinecone_index()

    # Convert search query to embedding
    query_embedding = model.encode(query).tolist()

    # Find most similar movies
    results = index.query(
        vector=query_embedding,
        top_k=limit,
        include_metadata=True
    )

    movies = []
    for match in results.get("matches", []):
        metadata = match.get("metadata", {})
        movies.append({
            "tmdb_id": int(match["id"]),
            "title": metadata.get("title"),
            "overview": metadata.get("overview"),
            "release_date": metadata.get("release_date"),
            "vote_average": metadata.get("vote_average"),
            "poster_url": metadata.get("poster_url"),
            "similarity_score": round(match["score"], 3)
        })

    return movies