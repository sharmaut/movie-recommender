# 🎬 Movie Recommender

A full-stack movie recommendation system that combines enterprise Java backend with a Python machine learning service and a React frontend. Users can search for similar movies, browse by genre and language, and receive personalised recommendations powered by Collaborative Filtering.

## Architecture

A polyglot microservices application — three independent services working together:

- **Java Spring Boot** — user management, JWT authentication, API routing
- **Python FastAPI** — machine learning recommendation engine
- **React** — frontend UI for browsing and searching movies
- **PostgreSQL** — stores users and viewing history
- **Pinecone** — vector database for semantic movie search
- **TMDB API** — real movie data, posters, descriptions

```
User → React Frontend (port 3000)
              ↓
       Python FastAPI (port 8000)
         ↓              ↓
   PostgreSQL       Pinecone
   (CF Model)    (Vector Search)
         ↓
      TMDB API
```

## Tech Stack

| Layer        | Technology                    | Purpose                             |
| ------------ | ----------------------------- | ----------------------------------- |
| Backend      | Java 21 / Spring Boot 3.5     | API, authentication, business logic |
| ML Engine    | Python 3.13 / FastAPI         | Recommendation algorithms           |
| Frontend     | React                         | Movie browsing and search UI        |
| Database     | PostgreSQL                    | Users and viewing history           |
| Vector DB    | Pinecone                      | Semantic similarity search          |
| ML Libraries | Scikit-learn / Pandas / NumPy | Collaborative Filtering             |
| Embeddings   | Sentence Transformers         | Movie text to vector conversion     |
| Security     | JWT / BCrypt                  | Authentication and password hashing |
| Movie Data   | TMDB API                      | Real movie metadata and posters     |

## Features

### 1. Similar Movie Search

Type any movie name and get similar movies back powered by TMDB's recommendation engine.

### 2. Genre, Language & Year Filter

Browse top rated movies by genre, language and decade. Supports 7 genres, 7 languages and 7 year ranges.

### 3. Collaborative Filtering Recommendations

- Builds a user-item matrix from viewing history
- Computes cosine similarity between users
- Recommends movies that similar users loved
- Handles new users with popularity fallback

### 4. Semantic Vector Search

- Converts movie descriptions into 384-dimensional embeddings using Sentence Transformers
- Stores embeddings in Pinecone vector database
- Search by vibe — finds thematically similar movies
- Available via API at `/vector/search`

## API Endpoints

### Java Backend (port 8080)

- `POST /api/auth/login` — returns JWT token
- `POST /api/users/register` — create account
- `GET /api/users/{email}` — get user (requires JWT)
- `GET /api/users/{userId}/recommendations` — ML recommendations

### Python ML Service (port 8000)

- `GET /health` — service status and model state
- `POST /recommendations` — collaborative filtering
- `POST /recommendations/detailed` — CF with full movie details
- `GET /recommendations/filter` — filter by genre, language and year
- `GET /recommendations/similar` — find similar movies by name
- `GET /vector/search` — semantic vector search
- `POST /vector/populate` — populate Pinecone with movies

## Running Locally

### Prerequisites

- Java 21
- Python 3.13
- PostgreSQL
- Node.js

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

### React Frontend

```bash
cd frontend
npm start
```

### Environment Variables

Create a `.env` file in `ml-service/`:

```
TMDB_API_KEY=your_tmdb_read_access_token
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX=movie-recommender
```

Add to `backend/src/main/resources/application.properties`:

```
spring.datasource.url=jdbc:postgresql://localhost:5432/movieapp
spring.datasource.username=your_username
spring.datasource.password=your_password
ml.service.url=http://localhost:8000
jwt.secret=your_secret_key
```

## What I Learned

- How to architect a polyglot microservices system
- How Collaborative Filtering and cosine similarity work mathematically
- How vector embeddings represent meaning numerically
- How JWT authentication works end to end
- How to connect three independent services over REST
