import { useState } from "react";

const GENRES = [
  { label: "Action", value: "action" },
  { label: "Comedy", value: "comedy" },
  { label: "Drama", value: "drama" },
  { label: "Horror", value: "horror" },
  { label: "Romance", value: "romance" },
  { label: "Sci-Fi", value: "scifi" },
  { label: "Thriller", value: "thriller" },
];

const LANGUAGES = [
  { label: "English", value: "en" },
  { label: "Hindi", value: "hi" },
  { label: "German", value: "de" },
  { label: "French", value: "fr" },
  { label: "Spanish", value: "es" },
  { label: "Japanese", value: "ja" },
  { label: "Korean", value: "ko" },
];

const YEAR_RANGES = [
  { label: "All Years", value: "" },
  { label: "2020 - Present", value: "2020,2026" },
  { label: "2010 - 2019", value: "2010,2019" },
  { label: "2000 - 2009", value: "2000,2009" },
  { label: "1990 - 1999", value: "1990,1999" },
  { label: "1980 - 1989", value: "1980,1989" },
  { label: "Before 1980", value: "1900,1979" },
];

function MovieCard({ movie }) {
  return (
    <div style={styles.card}>
      {movie.poster_url ? (
        <img src={movie.poster_url} alt={movie.title} style={styles.poster} />
      ) : (
        <div style={styles.noPoster}>No Poster</div>
      )}
      <div style={styles.cardBody}>
        <h3 style={styles.title}>{movie.title}</h3>
        <p style={styles.rating}>⭐ {movie.vote_average?.toFixed(1)}</p>
        <p style={styles.year}>{movie.release_date?.split("-")[0]}</p>
        <p style={styles.overview}>
          {movie.overview?.length > 150
            ? movie.overview.substring(0, 150) + "..."
            : movie.overview}
        </p>
      </div>
    </div>
  );
}

export default function App() {
  const [searchQuery, setSearchQuery] = useState("");
  const [genre, setGenre] = useState("action");
  const [language, setLanguage] = useState("en");
  const [yearRange, setYearRange] = useState("");
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [heading, setHeading] = useState("");

  const searchSimilar = async () => {
    if (!searchQuery.trim()) return;
    setLoading(true);
    setError("");
    try {
      const res = await fetch(
        `/recommendations/similar?movie_name=${encodeURIComponent(searchQuery)}&limit=20`
      );
      const data = await res.json();
      setMovies(data.similar_movies || []);
      setHeading(`Movies similar to "${data.searched_movie}"`);
    } catch (err) {
      setError("Something went wrong. Make sure the ML service is running.");
    }
    setLoading(false);
  };

  const filterMovies = async () => {
    setLoading(true);
    setError("");
    try {
      let url = `/recommendations/filter?genre=${genre}&language=${language}&limit=20`;
      if (yearRange) {
        const [from, to] = yearRange.split(",");
        url += `&year_from=${from}&year_to=${to}`;
      }
      const res = await fetch(url);
      const data = await res.json();
      if (data.movies?.length === 0) {
        setError("No movies found for this combination. Try another.");
        setMovies([]);
      } else {
        setMovies(data.movies);
        setHeading(`Top ${data.movies.length} ${genre} movies`);
      }
    } catch (err) {
      setError("Something went wrong. Make sure the ML service is running.");
    }
    setLoading(false);
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.header}>🎬 Movie Recommender</h1>

      {/* Search Section */}
      <div style={styles.section}>
        <h2 style={styles.sectionTitle}>Find Similar Movies</h2>
        <div style={styles.row}>
          <input
            style={styles.input}
            type="text"
            placeholder="Enter a movie name..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && searchSimilar()}
          />
          <button style={styles.button} onClick={searchSimilar}>
            Search
          </button>
        </div>
      </div>

      {/* Filter Section */}
      <div style={styles.section}>
        <h2 style={styles.sectionTitle}>Browse by Genre, Language & Year</h2>
        <div style={styles.row}>
          <select
            style={styles.select}
            value={genre}
            onChange={(e) => setGenre(e.target.value)}
          >
            {GENRES.map((g) => (
              <option key={g.value} value={g.value}>
                {g.label}
              </option>
            ))}
          </select>
          <select
            style={styles.select}
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
          >
            {LANGUAGES.map((l) => (
              <option key={l.value} value={l.value}>
                {l.label}
              </option>
            ))}
          </select>
          <select
            style={styles.select}
            value={yearRange}
            onChange={(e) => setYearRange(e.target.value)}
          >
            {YEAR_RANGES.map((y) => (
              <option key={y.value} value={y.value}>
                {y.label}
              </option>
            ))}
          </select>
          <button style={styles.button} onClick={filterMovies}>
            Find Movies
          </button>
        </div>
      </div>

      {/* Results */}
      {loading && <p style={styles.loading}>Loading...</p>}
      {error && <p style={styles.error}>{error}</p>}
      {movies.length > 0 && (
        <>
          <h2 style={styles.resultsHeading}>{heading}</h2>
          <div style={styles.grid}>
            {movies.map((movie) => (
              <MovieCard key={movie.tmdb_id} movie={movie} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}

const styles = {
  container: {
    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    minHeight: "100vh",
    padding: "20px 40px",
    fontFamily: "'Arial', sans-serif",
    color: "#1a1a2e",
  },
  header: {
    textAlign: "center",
    fontSize: "2.8rem",
    color: "#ffffff",
    marginBottom: "30px",
    letterSpacing: "2px",
    textShadow: "0 2px 10px rgba(0,0,0,0.3)",
  },
  section: {
    backgroundColor: "#ffffff",
    borderRadius: "20px",
    padding: "24px",
    marginBottom: "20px",
    boxShadow: "0 8px 32px rgba(0,0,0,0.15)",
  },
  sectionTitle: {
    fontSize: "1.2rem",
    marginBottom: "15px",
    color: "#764ba2",
    fontWeight: "bold",
  },
  row: {
    display: "flex",
    gap: "10px",
    flexWrap: "wrap",
    alignItems: "center",
  },
  input: {
    flex: 1,
    padding: "12px 18px",
    borderRadius: "12px",
    border: "2px solid #e0e7ff",
    fontSize: "1rem",
    backgroundColor: "#f8f9ff",
    color: "#1a1a2e",
    minWidth: "200px",
    outline: "none",
  },
  select: {
    padding: "12px 18px",
    borderRadius: "12px",
    border: "2px solid #e0e7ff",
    fontSize: "1rem",
    backgroundColor: "#f8f9ff",
    color: "#1a1a2e",
    cursor: "pointer",
    outline: "none",
  },
  button: {
    padding: "12px 28px",
    background: "linear-gradient(135deg, #667eea, #764ba2)",
    color: "#fff",
    border: "none",
    borderRadius: "12px",
    fontSize: "1rem",
    cursor: "pointer",
    fontWeight: "bold",
    boxShadow: "0 4px 15px rgba(102, 126, 234, 0.5)",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))",
    gap: "20px",
    marginTop: "20px",
  },
  card: {
    backgroundColor: "#ffffff",
    borderRadius: "16px",
    overflow: "hidden",
    boxShadow: "0 8px 25px rgba(0,0,0,0.12)",
    transition: "transform 0.2s",
  },
  poster: {
    width: "100%",
    height: "300px",
    objectFit: "cover",
  },
  noPoster: {
    width: "100%",
    height: "300px",
    background: "linear-gradient(135deg, #667eea, #764ba2)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    color: "#ffffff",
    fontSize: "0.9rem",
  },
  cardBody: {
    padding: "12px",
  },
  title: {
    fontSize: "0.95rem",
    marginBottom: "5px",
    color: "#1a1a2e",
    fontWeight: "bold",
  },
  rating: {
    color: "#f59e0b",
    fontSize: "0.85rem",
    marginBottom: "3px",
    fontWeight: "bold",
  },
  year: {
    color: "#6b7280",
    fontSize: "0.8rem",
    marginBottom: "5px",
  },
  overview: {
    fontSize: "0.75rem",
    color: "#6b7280",
    lineHeight: "1.4",
  },
  loading: {
    textAlign: "center",
    fontSize: "1.2rem",
    color: "#ffffff",
    fontWeight: "bold",
  },
  error: {
    textAlign: "center",
    color: "#ff6b6b",
    fontSize: "1rem",
    fontWeight: "bold",
    backgroundColor: "rgba(255,255,255,0.9)",
    padding: "10px",
    borderRadius: "10px",
  },
  resultsHeading: {
    fontSize: "1.3rem",
    marginBottom: "10px",
    color: "#ffffff",
    fontWeight: "bold",
    textShadow: "0 2px 8px rgba(0,0,0,0.2)",
  },
};