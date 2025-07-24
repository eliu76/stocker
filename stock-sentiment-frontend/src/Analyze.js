/* analyze stock web page that allows user to choose which stock to scrape the web for sentiment for and generate a reccomendation*/

import React, { useState } from "react";
import StockPerformanceChart from "./chart";

function AnalyzePage() {
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
    <div>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Ticker (e.g., AAPL)"
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
        />

        <input
          type="text"
          placeholder="Company Name (e.g., Apple)"
          value={companyName}
          onChange={(e) => setCompanyName(e.target.value)}
        />

        <button type="submit" disabled={loading}>
          {loading ? "Analyzing..." : "Analyze"}
        </button>
      </form>

      {error && <p className="error-message">Error: {error}</p>}

      {result && (
        <section className="results" aria-live="polite">
          <h2>Results for {result.company_name || result.ticker}</h2>

          <h3>Sentiment Summary</h3>
          <p>{result.sentiment_result.summary}</p>

          <h3>Overall Sentiment</h3>
          <p>{result.sentiment_result.overall_sentiment}</p>

          <h3>Explanation</h3>
          <pre>{result.explanation}</pre>

          <h3>Rule-Based Recommendation</h3>
          <p>
            <strong>{result.recommendation.recommendation}</strong> — {result.recommendation.reasoning}
          </p>

          <h3>LLM-Based Recommendation (Groq)</h3>
          <p>
            <strong>{result.llm_recommendation.recommendation}</strong> — {result.llm_recommendation.reasoning}
          </p>

          {result.performance_simulation && !result.performance_simulation.error && (
            <>
              <h3> Simulated 30-Day Return</h3>
              <ul>
                <li>Start Price: ${result.performance_simulation.start_price.toFixed(2)}</li>
                <li>End Price: ${result.performance_simulation.end_price.toFixed(2)}</li>
                <li>
                  Simulated Return:&nbsp;
                  <strong style={{ color: result.performance_simulation.simulated_return_pct >= 0 ? "green" : "red" }}>
                    {result.performance_simulation.simulated_return_pct.toFixed(2)}%
                  </strong>
                </li>
              </ul>
              <StockPerformanceChart prices={result.historical_prices} ticker={result.ticker} />
            </>
          )}

          {result.performance_simulation?.error && (
            <p style={{ color: "gray" }}>
              Could not simulate performance: {result.performance_simulation.error}
            </p>
          )}
        </section>
      )}
    </div>
  );
}

export default AnalyzePage;
