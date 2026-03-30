package com.movierecommender.backend.entity;

import jakarta.persistence.*;

import java.time.Instant;

@Entity
@Table(name = "viewing_history")
public class ViewingHistory {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @Column(name = "tmdb_movie_id", nullable = false)
    private Long tmdbMovieId;

    @Column(name = "watched_at", updatable = false)
    private Instant watchedAt;

    @Column
    private Double rating;

    @PrePersist
    protected void onCreate() {
        this.watchedAt = Instant.now();
    }

    public Long getId() { return id; }

    public User getUser() { return user; }
    public void setUser(User user) { this.user = user; }

    public Long getTmdbMovieId() { return tmdbMovieId; }
    public void setTmdbMovieId(Long tmdbMovieId) { this.tmdbMovieId = tmdbMovieId; }

    public Instant getWatchedAt() { return watchedAt; }

    public Double getRating() { return rating; }
    public void setRating(Double rating) { this.rating = rating; }
}
