package com.movierecommender.backend.controller;

import com.movierecommender.backend.entity.User;
import com.movierecommender.backend.entity.ViewingHistory;
import com.movierecommender.backend.repository.ViewingHistoryRepository;
import com.movierecommender.backend.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import com.movierecommender.backend.client.RecommendationClient;

import java.util.List;

@RestController
@RequestMapping("/api/users")
public class UserController {

    private final UserService userService;

    @Autowired
    private RecommendationClient recommendationClient;

    @Autowired
    private ViewingHistoryRepository viewingHistoryRepository;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @PostMapping("/register")
    public ResponseEntity<User> register(@RequestBody RegisterRequest request) {
        User user = userService.registerUser(
                request.name(),
                request.email(),
                request.password()
        );
        return ResponseEntity.ok(user);
    }

    @GetMapping("/{email}")
    public ResponseEntity<User> getUser(@PathVariable String email) {
        User user = userService.findByEmail(email);
        return ResponseEntity.ok(user);
    }

    @GetMapping("/{userId}/recommendations")
    public ResponseEntity<List<Integer>> getRecommendations(@PathVariable Long userId) {
        List<ViewingHistory> history = viewingHistoryRepository.findByUserId(userId);
        List<Long> watchedIds = history.stream()
                .map(ViewingHistory::getTmdbMovieId)
                .toList();

        List<Integer> recommendations = recommendationClient.getRecommendations(
                userId, watchedIds, 10);
        return ResponseEntity.ok(recommendations);
    }

    public record RegisterRequest(String name, String email, String password) {}
}
