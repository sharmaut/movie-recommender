package com.movierecommender.backend.service;

import com.movierecommender.backend.entity.User;
import com.movierecommender.backend.repository.UserRepository;
import org.springframework.stereotype.Service;

@Service
public class UserService {

    private final UserRepository userRepository;

    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    public User registerUser(String name, String email, String password) {
        if (userRepository.existsByEmail(email)) {
            throw new RuntimeException("Email already in use");
        }

        User user = new User();
        user.setName(name);
        user.setEmail(email);
        user.setPassword(password);

        return userRepository.save(user);
    }

        public User findByEmail(String email) {
            return userRepository.findByEmail((email))
                    .orElseThrow(() -> new RuntimeException("User not found"));
    }
}
