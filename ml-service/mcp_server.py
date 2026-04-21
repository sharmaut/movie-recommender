import asyncio
import httpx
import os
from pathlib import Path
from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

load_dotenv(Path(__file__).parent / ".env")

app = Server("movie-recommender")

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """Define the tools Claude can use from your movie recommender."""
    return [
        types.Tool(
            name="search_similar_movies",
            description="Find movies similar to a specific movie the user mentions. Use this when the user names a specific movie.",
            inputSchema={
                "type": "object",
                "properties": {
                    "movie_name": {
                        "type": "string",
                        "description": "The name of the movie to find similar movies for"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of movies to return",
                        "default": 5
                    }
                },
                "required": ["movie_name"]
            }
        ),
        types.Tool(
            name="filter_movies",
            description="Browse top rated movies by genre and language. Use this when the user mentions a specific genre or language.",
            inputSchema={
                "type": "object",
                "properties": {
                    "genre": {
                        "type": "string",
                        "description": "Movie genre: action, comedy, drama, horror, romance, scifi, thriller",
                    },
                    "language": {
                        "type": "string",
                        "description": "Language code: en, hi, de, fr, es, ja, ko",
                        "default": "en"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of movies to return",
                        "default": 5
                    }
                },
                "required": ["genre"]
            }
        ),
        types.Tool(
            name="get_recommendations",
            description="Get personalised movie recommendations for a user based on their viewing history using collaborative filtering.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "The user ID to get recommendations for"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of recommendations to return",
                        "default": 5
                    }
                },
                "required": ["user_id"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    base_url = "http://127.0.0.1:8000"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:

            if name == "search_similar_movies":
                response = await client.get(
                    f"{base_url}/recommendations/similar",
                    params={
                        "movie_name": arguments["movie_name"],
                        "limit": arguments.get("limit", 5)
                    }
                )
                data = response.json()
                movies = data.get("similar_movies", [])
                searched = data.get("searched_movie", arguments["movie_name"])

                result = f"Movies similar to '{searched}':\n\n"
                for i, movie in enumerate(movies, 1):
                    result += f"{i}. {movie['title']} ({movie.get('release_date', '')[:4]})\n"
                    result += f"   Rating: {movie.get('vote_average', 'N/A')}/10\n"
                    result += f"   {movie.get('overview', '')[:150]}...\n\n"
                return [types.TextContent(type="text", text=result)]

            elif name == "filter_movies":
                response = await client.get(
                    f"{base_url}/recommendations/filter",
                    params={
                        "genre": arguments["genre"],
                        "language": arguments.get("language", "en"),
                        "limit": arguments.get("limit", 5)
                    }
                )
                data = response.json()
                movies = data.get("movies", [])

                result = f"Top {arguments['genre']} movies:\n\n"
                for i, movie in enumerate(movies, 1):
                    result += f"{i}. {movie['title']} ({movie.get('release_date', '')[:4]})\n"
                    result += f"   Rating: {movie.get('vote_average', 'N/A')}/10\n"
                    result += f"   {movie.get('overview', '')[:150]}...\n\n"
                return [types.TextContent(type="text", text=result)]

            elif name == "get_recommendations":
                response = await client.post(
                    f"{base_url}/recommendations/detailed",
                    json={
                        "user_id": arguments["user_id"],
                        "watched_movie_ids": [],
                        "limit": arguments.get("limit", 5)
                    }
                )
                data = response.json()
                movies = data.get("recommendations", [])

                if not movies:
                    return [types.TextContent(type="text", text="No recommendations found for this user.")]

                result = f"Recommendations for user {arguments['user_id']}:\n\n"
                for i, movie in enumerate(movies, 1):
                    result += f"{i}. {movie['title']} ({movie.get('release_date', '')[:4]})\n"
                    result += f"   Rating: {movie.get('vote_average', 'N/A')}/10\n"
                    result += f"   {movie.get('overview', '')[:150]}...\n\n"
                return [types.TextContent(type="text", text=result)]

            else:
                return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        return [types.TextContent(type="text", text=f"Error calling movie service: {str(e)}. Make sure uvicorn is running on port 8000.")]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())