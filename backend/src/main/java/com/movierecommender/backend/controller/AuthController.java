package com.movierecommender.backend.controller;

import com.movierecommender.backend.config.JwtUtil;
import com.movierecommender.backend.entity.User;
import com.movierecommender.backend.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    @Autowired
    private UserService userService;

    @Autowired
    private JwtUtil jwtUtil;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody LoginRequest request) {
        try {
            User user = userService.findByEmail(request.email());

            if (!passwordEncoder.matches(request.password(), user.getPassword())) {
                return ResponseEntity.status(401).body("Invalid password");
            }

            String token = jwtUtil.generateToken(user.getEmail());
            return ResponseEntity.ok(new LoginResponse(token, user.getId(), user.getEmail()));

        } catch (RuntimeException e) {
            return ResponseEntity.status(401).body("User not found");
        }
    }

    public record LoginRequest(String email, String password) {}

    public record LoginResponse(String token, Long userId, String email) {}
}