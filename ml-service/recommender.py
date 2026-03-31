import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

class CollaborativeFilter:

    def __init__(self):
        self.user_item_matrix = None
        self.similarity_matrix = None
    
    def fit(self, ratings_data: list[dict]):
        """
        Train the model on viewing history data.
        ratings_data: list of dicts with user_id, tmdb_movie_id, rating
        """
        df = pd.DataFrame(ratings_data)

        self.user_item_matrix = df.pivot_table(
            index="user_id",
            columns="tmdb_movie_id",
            values="rating",
            aggfunc="mean"
        ).fillna(0)

        self.similarity_matrix = cosine_similarity(self.user_item_matrix.values)
        logger.info("Model trained on %d users and %d movies",
                   self.user_item_matrix.shape[0],
                   self.user_item_matrix.shape[1])

    def recommend(self, user_id: int, watched_ids: list[int], limit: int = 10):
        """
        Return top N recommended movie IDs for a user.
        Falls back to popularity if user not in training data.
        """
        if self.user_item_matrix is None:
            logger.warning("Model not trained yet")
            return [], []

        if user_id not in self.user_item_matrix.index:
            logger.info("Cold start user %d - using popularity fallback", user_id)
            return self._popularity_fallback(watched_ids, limit)

        user_idx = self.user_item_matrix.index.get_loc(user_id)
        sim_scores = self.similarity_matrix[user_idx]
        similar_users = np.argsort(sim_scores)[::-1][1:21]

        similar_ratings = self.user_item_matrix.iloc[similar_users]
        weights = sim_scores[similar_users]
        weighted_scores = np.average(similar_ratings.values, axis=0, weights=weights)

        scores = pd.Series(weighted_scores, index=self.user_item_matrix.columns)
        scores = scores.drop(labels=[m for m in watched_ids if m in scores.index],
                            errors="ignore")

        top = scores.nlargest(limit)
        return top.index.tolist(), top.values.tolist()

    def _popularity_fallback(self, exclude_ids: list[int], limit: int):
        """For new users with no history - return most watched movies."""
        popularity = (self.user_item_matrix > 0).sum(axis=0)
        popularity = popularity.drop(
            labels=[m for m in exclude_ids if m in popularity.index],
            errors="ignore"
        )
        top = popularity.nlargest(limit)
        max_val = top.max() or 1
        scores = (top.values / max_val).tolist()
        return top.index.tolist(), scores