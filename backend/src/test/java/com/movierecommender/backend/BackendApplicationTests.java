package com.movierecommender.backend;

import com.movierecommender.backend.config.JwtUtil;
import com.movierecommender.backend.entity.User;
import com.movierecommender.backend.repository.UserRepository;
import com.movierecommender.backend.service.UserService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class BackendApplicationTests {

	@Autowired
	private UserService userService;

	@Autowired
	private UserRepository userRepository;

	@Autowired
	private JwtUtil jwtUtil;

	@Test
	void registerUser_savesUserToDatabase() {
		String email = "testuser_" + System.currentTimeMillis() + "@test.com";

		User user = userService.registerUser("Test User", email, "password123");

		assertNotNull(user.getId());
		assertEquals(email, user.getEmail());
		assertNotEquals("password123", user.getPassword()); // password must be hashed

		userRepository.deleteById(user.getId());
	}

	@Test
	void registerUser_throwsException_whenEmailAlreadyExists() {
		RuntimeException exception = assertThrows(RuntimeException.class, () -> {
			userService.registerUser("Utsav", "utsav@test.com", "password123");
		});

		assertEquals("Email already in use", exception.getMessage());
	}

	@Test
	void jwtUtil_generatesAndValidatesToken() {
		String email = "jwt@test.com";

		String token = jwtUtil.generateToken(email);

		assertNotNull(token);
		assertTrue(jwtUtil.isTokenValid(token));
		assertEquals(email, jwtUtil.extractEmail(token));
	}
}