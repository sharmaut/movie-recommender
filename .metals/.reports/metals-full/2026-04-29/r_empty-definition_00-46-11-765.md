error id: file://<HOME>/Documents/Projects/Personal%20Projects/movie-recommender/backend/src/test/java/com/movierecommender/backend/BackendApplicationTests.java:
file://<HOME>/Documents/Projects/Personal%20Projects/movie-recommender/backend/src/test/java/com/movierecommender/backend/BackendApplicationTests.java
empty definition using pc, found symbol in pc: 
empty definition using semanticdb
empty definition using fallback
non-local guesses:

offset: 1395
uri: file://<HOME>/Documents/Projects/Personal%20Projects/movie-recommender/backend/src/test/java/com/movierecommender/backend/BackendApplicationTests.java
text:
```scala
package com.movierecommender.backend;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import com.movierecommender.backend.config.JwtUtil;
import com.movierecommender.backend.entity.User;
import com.movierecommender.backend.repository.UserRepository;
import com.movierecommender.backend.service.UserService;

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
    String@@ email = "duplicate_" + System.currentTimeMillis() + "@test.com";

    userService.registerUser("First User", email, "password123");

    RuntimeException exception = assertThrows(RuntimeException.class, () -> {
        userService.registerUser("Second User", email, "password123");
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
```


#### Short summary: 

empty definition using pc, found symbol in pc: 