# 🎬 Movie Recommender

A movie recommendation system built with Java Spring Boot and Python FastAPI. Java handles users and authentication, Python runs a Collaborative Filtering algorithm that suggests movies based on what similar users watched.

## Architecture

This is a polyglot microservices application — two independent services built with the best tool for each job:

- **Java Spring Boot** handles user management, authentication, and API routing
- **Python FastAPI** runs the machine learning recommendation engine
- **PostgreSQL** stores users, and viewing history
- Both services communicate via REST/JSON

```
User Request
     ↓
Java Spring Boot (port 8080)
     ↓ fetches watch history from PostgreSQL
     ↓ calls Python service
Python FastAPI (port 8000)
     ↓ runs Collaborative Filtering
     ↓ returns recommended movie IDs
Java returns recommendations to user
```

## Tech Stack

| Layer        | Technology                    | Purpose                             |
| ------------ | ----------------------------- | ----------------------------------- |
| Backend      | Java 21 / Spring Boot 3.5     | API, authentication, business logic |
| ML Engine    | Python 3.13 / FastAPI         | Recommendation algorithm            |
| Database     | PostgreSQL                    | Users and viewing history           |
| ML Libraries | Scikit-learn / Pandas / NumPy | Collaborative Filtering             |
| Security     | JWT / BCrypt                  | Authentication and password hashing |

## How the Recommendation Engine Works

The ML service uses **User-Based Collaborative Filtering**:

1. Builds a user-item matrix from viewing history — rows are users, columns are movies, values are ratings
2. Computes **cosine similarity** between every pair of users
3. For a target user, finds the most similar users
4. Recommends movies those similar users loved that the target user hasn't seen yet
5. Falls back to popularity ranking for new users with no history (cold start problem)

## API Endpoints

### Auth

- `POST /api/auth/login` — returns a JWT token

### Users

- `POST /api/users/register` — create a new account
- `GET /api/users/{email}` — get user by email (requires JWT)
- `GET /api/users/{userId}/recommendations` — get ML recommendations (requires JWT)

### ML Service

- `GET /health` — service health + model status
- `POST /recommendations` — get recommendations for a user

## Running Locally

### Prerequisites

- Java 21
- Python 3.13
- PostgreSQL

### Java Backend

```bash
cd backend
./mvnw spring-boot:run
```

### Python ML Service

```bash
cd ml-service
source venv/bin/activate
python3 -m uvicorn main:app --reload --port 8000
```

## What I Learned

- How to architect a polyglot microservices system
- How Collaborative Filtering and cosine similarity work mathematically
- How JWT authentication works end to end
- How to connect two independent services over REST
