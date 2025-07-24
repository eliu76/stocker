/* react home page */

import React, { useState } from "react";
import "./App.css";
import AnalyzePage from "./Analyze";
import Watchlist from "./Watchlist";

function App() {
  const [activeTab, setActiveTab] = useState("analyze");

  return (
    <div className="App">
      <h1>Stock Sentiment Analyzer</h1>

      <div className="tab-buttons">
        <button onClick={() => setActiveTab("analyze")} className={activeTab === "analyze" ? "active" : ""}>
          Analyze
        </button>
        <button onClick={() => setActiveTab("watchlist")} className={activeTab === "watchlist" ? "active" : ""}>
          Watchlist
        </button>
      </div>

      <hr />

      {activeTab === "analyze" ? <AnalyzePage /> : <Watchlist />}
    </div>
  );
}

export default App;
