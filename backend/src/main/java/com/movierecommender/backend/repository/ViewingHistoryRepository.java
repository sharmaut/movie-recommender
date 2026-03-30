package com.movierecommender.backend.repository;

import com.movierecommender.backend.entity.ViewingHistory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface ViewingHistoryRepository extends JpaRepository<ViewingHistory, Long> {

    List<ViewingHistory> findByUserId(Long userId);

    boolean existsByUserIdAndTmdbMovieId(Long userId, Long tmdbMovieId);
}
