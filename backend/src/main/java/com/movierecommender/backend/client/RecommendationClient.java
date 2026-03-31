package com.movierecommender.backend.client;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.ResponseEntity;
import java.util.List;

@Component
public class RecommendationClient {

    private final RestTemplate restTemplate;
    private final String mlServiceUrl;

    public RecommendationClient(@Value("${ml.service.url}") String mlServiceUrl) {
        this.restTemplate = new RestTemplate();
        this.mlServiceUrl = mlServiceUrl;
    }

    public List<Integer> getRecommendations(Long userId, List<Long> watchedMovieIds, int limit) {
        String url = mlServiceUrl + "/recommendations";

        RecommendationRequest request = new RecommendationRequest(userId, watchedMovieIds, limit);

        try {
            ResponseEntity<RecommendationResponse> response = restTemplate.postForEntity(
                    url,
                    request,
                    RecommendationResponse.class
            );

            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                return response.getBody().recommendedMovieIds();
            }

        } catch (Exception e) {
            System.err.println("ML service call failed: " + e.getMessage());
        }

        return List.of();
    }

    public record RecommendationRequest(
            @com.fasterxml.jackson.annotation.JsonProperty("user_id") Long userId,
            @com.fasterxml.jackson.annotation.JsonProperty("watched_movie_ids") List<Long> watchedMovieIds,
            int limit
    ) {}

    public record RecommendationResponse(
            @com.fasterxml.jackson.annotation.JsonProperty("user_id") Long userId,
            @com.fasterxml.jackson.annotation.JsonProperty("recommended_movie_ids") List<Integer> recommendedMovieIds,
            @com.fasterxml.jackson.annotation.JsonProperty("model_version") String modelVersion,
            @com.fasterxml.jackson.annotation.JsonProperty("confidence_scores") List<Double> confidenceScores
    ) {}
}