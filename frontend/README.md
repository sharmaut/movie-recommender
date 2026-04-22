# 🎬 Movie Recommender

A full-stack movie recommendation system using Java Spring Boot, Python FastAPI, and React. Implements Collaborative Filtering with cosine similarity, Pinecone vector search, Claude API for AI-powered smart search, and an MCP server for agentic workflows.

## Architecture

```
User → React Frontend (port 3000)
              ↓
       Python FastAPI (port 8000)
         ↓         ↓          ↓
   PostgreSQL   Pinecone   Claude API
   (CF Model)  (Vectors)  (Smart Search)
         ↓
      TMDB API
```

## Tech Stack

| Layer          | Technology                    | Purpose                                |
| -------------- | ----------------------------- | -------------------------------------- |
| Backend        | Java 21 / Spring Boot 3.5     | API, authentication, business logic    |
| ML Engine      | Python 3.13 / FastAPI         | Recommendation algorithms              |
| Frontend       | React                         | Movie browsing and search UI           |
| Database       | PostgreSQL                    | Users and viewing history              |
| Vector DB      | Pinecone                      | Semantic similarity search             |
| AI Integration | Claude API                    | Natural language query understanding   |
| MCP Server     | Model Context Protocol        | Agentic tool access via Claude Desktop |
| ML Libraries   | Scikit-learn / Pandas / NumPy | Collaborative Filtering                |
| Embeddings     | Sentence Transformers         | Movie text to vector conversion        |
| Security       | JWT / BCrypt                  | Authentication and password hashing    |
| Movie Data     | TMDB API                      | Real movie metadata and posters        |

## Features

### 1. Smart Search — powered by Claude API

Type natural language queries like "dark thriller from the 90s" or "feel good Korean comedy." Claude interprets the query, extracts genre, language, mood, and year range, then routes to the right search method automatically.

### 2. Collaborative Filtering Recommendations

Builds a user-item matrix from viewing history, computes cosine similarity between users, and recommends movies that similar users loved. Handles new users with a popularity fallback.

### 3. Genre, Language & Year Filter

Browse top rated movies by genre, language and decade. Supports 7 genres, 7 languages and 7 year ranges powered by TMDB Discover API.

### 4. Similar Movie Search

Type any movie name and get similar movies back powered by TMDB's recommendation engine.

### 5. Semantic Vector Search

Converts movie descriptions into 384-dimensional embeddings using Sentence Transformers. Stores embeddings in Pinecone for semantic similarity search. Available via API.

### 6. MCP Server — Agentic Workflows

Exposes the movie recommender as tools that Claude Desktop can call autonomously. Claude decides which tool to use based on natural language input — search similar movies, filter by genre, or get personalised recommendations.

## API Endpoints

### Java Backend (port 8080)

- `POST /api/auth/login` — returns JWT token
- `POST /api/users/register` — create account
- `GET /api/users/{email}` — get user (requires JWT)
- `GET /api/users/{userId}/recommendations` — ML recommendations

### Python ML Service (port 8000)

- `GET /health` — service status
- `GET /recommendations/smart` — Claude AI powered natural language search
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
- Claude Desktop (for MCP)

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
ANTHROPIC_API_KEY=your_anthropic_api_key
```

## What I Learned

- How to architect a polyglot microservices system
- How Collaborative Filtering and cosine similarity work mathematically
- How vector embeddings represent meaning numerically
- How to integrate the Claude API for natural language understanding
- How to build an MCP server for agentic AI workflows
- How JWT authentication works end to end
- How to connect three independent services over REST
