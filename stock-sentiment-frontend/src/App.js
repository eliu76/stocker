import React, { useState } from "react";

function App() {
  const [ticker, setTicker] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    setError("");

    try {
      const response = await fetch("http://127.0.0.1:5000/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ticker: ticker.trim().toUpperCase(),
          company_name: companyName.trim(),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Something went wrong");
      }

      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 700, margin: "2rem auto", padding: "0 1rem" }}>
      <h1>Stock Sentiment Analyzer</h1>

      <form onSubmit={handleSubmit} style={{ marginBottom: "1.5rem" }}>
        <input
          type="text"
          placeholder="Ticker (e.g., AAPL)"
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
          style={{ width: "100%", padding: "0.5rem", marginBottom: "0.5rem" }}
        />

        <input
          type="text"
          placeholder="Company Name (e.g., Apple)"
          value={companyName}
          onChange={(e) => setCompanyName(e.target.value)}
          style={{ width: "100%", padding: "0.5rem", marginBottom: "0.5rem" }}
        />

        <button type="submit" disabled={loading} style={{ padding: "0.5rem 1rem" }}>
          {loading ? "Analyzing..." : "Analyze"}
        </button>
      </form>

      {error && <p style={{ color: "red" }}>Error: {error}</p>}

      {result && (
        <div>
          <h2>Results for {result.company_name || result.ticker}</h2>

          <h3>Sentiment Summary</h3>
          <p>{result.sentiment_result.summary}</p>

          <h3>Overall Sentiment</h3>
          <p>{result.sentiment_result.overall_sentiment}</p>

          <h3>Explanation</h3>
          <pre style={{ whiteSpace: "pre-wrap" }}>{result.explanation}</pre>

          <h3>Recommendation</h3>
          <p>
            <strong>{result.recommendation.recommendation}</strong> — {result.recommendation.reasoning}
          </p>
        </div>
      )}
    </div>
  );
}

export default App;
