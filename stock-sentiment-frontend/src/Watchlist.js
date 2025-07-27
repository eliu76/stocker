/* watchlist web page that displays current watchlist, allows for insertion/deletion,
   stock price graph visual, and manual digest email sending */

import React, { useState, useEffect } from "react";
import StockPerformanceChart from "./chart";

const Watchlist = () => {
  const [performanceData, setPerformanceData] = useState([]);
  const [newTicker, setNewTicker] = useState("");
  const [error, setError] = useState("");
  const userId = "guest";

  useEffect(() => {
    fetchPerformanceData();
  }, []);

  const fetchPerformanceData = async () => {
    try {
      setError("");
      const response = await fetch(`http://localhost:5000/api/watchlist/performance?user_id=${userId}`);
      const data = await response.json();

      if (Array.isArray(data)) {
        setPerformanceData(data);
      } else if (data.error) {
        setError(data.error);
        setPerformanceData([]);
      } else {
        setError("Unexpected data format received");
        setPerformanceData([]);
      }
    } catch (err) {
      setError("Failed to load watchlist performance data");
      setPerformanceData([]);
      console.error("Failed to load watchlist performance data:", err);
    }
  };

  const handleAddTicker = async () => {
    if (!newTicker.trim()) return;

    try {
      setError("");
      const response = await fetch("http://localhost:5000/api/watchlist/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: userId,
          ticker: newTicker.trim().toUpperCase(),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.error || "Failed to add ticker");
        return;
      }

      setNewTicker("");
      await fetchPerformanceData();
    } catch (err) {
      setError("Failed to add ticker");
      console.error(err);
    }
  };

  const handleDelete = async (id) => {
    try {
      setError("");
      const response = await fetch(`http://localhost:5000/api/watchlist/${id}`, {
        method: "DELETE",
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.error || "Failed to delete ticker");
        return;
      }

      await fetchPerformanceData();
    } catch (err) {
      setError("Failed to delete ticker");
      console.error(err);
    }
  };

const handleSendDigest = async () => {
  try {
    setError("");
    const response = await fetch("http://localhost:5000/api/digest/send", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ user_id: userId }),
    });

    const data = await response.json();

    if (!response.ok) {
      setError(data.error || "Failed to send digest");
      return;
    }

    alert("Digest email has been sent successfully!");
  } catch (err) {
    setError("Failed to send digest email");
    console.error(err);
  }
};

  return (
    <div className="watchlist">
      <h2>Watchlist</h2>

      <div>
        <input
          type="text"
          value={newTicker}
          onChange={(e) => setNewTicker(e.target.value)}
          placeholder="Add ticker (e.g. AAPL)"
        />
        <button style={{ marginLeft: "0.5rem" }} onClick={handleAddTicker}>Add</button>
      </div>

      <button
        style={{
          marginTop: "1rem",
          backgroundColor: "#4CAF50",
          color: "white",
          padding: "8px 12px",
          border: "none",
          cursor: "pointer",
          borderRadius: "4px",
        }}
        onClick={handleSendDigest}
      >
        Send me my daily digest email
      </button>

      {error && <p style={{ color: "red" }}>Error: {error}</p>}

      {performanceData.length === 0 && !error ? (
        <p>No tickers in your watchlist yet.</p>
      ) : (
        <ul>
          {performanceData.map((item) => (
            <li key={item.ticker} style={{ marginBottom: "2rem" }}>
              <strong>{item.ticker}</strong>
              <button
                style={{ marginLeft: "1rem", backgroundColor: "#d41a1aff", color: "white", border: "none", padding: "4px 8px", borderRadius: "3px", cursor: "pointer" }}
                onClick={() => handleDelete(item.id)}
              >
                Remove
              </button>

              <StockPerformanceChart prices={item.prices} ticker={item.ticker} />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default Watchlist;
