import psycopg2
import logging

logger = logging.getLogger(__name__)

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "movieapp",
    "user": "utsavsharma",
    "password": ""
}

def get_viewing_history():
    """
    Fetch all viewing history from PostgreSQL.
    Returns a list of dicts with user_id, tmdb_movie_id, rating.
    This is the raw data the ML model trains on.
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT user_id, tmdb_movie_id, rating
            FROM viewing_history
            WHERE rating IS NOT NULL
        """)

        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        data = [
            {
                "user_id": row[0],
                "tmdb_movie_id": row[1],
                "rating": float(row[2])
            }
            for row in rows
        ]

        logger.info("Fetched %d viewing history records", len(data))
        return data

    except Exception as e:
        logger.error("Database error: %s", e)
        return []