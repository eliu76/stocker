# has two classes: 
# fetch_historical_prices: fetches prices for a ticker using yfinance
# simulate_perforamance: based on recommendation passed in, simulates what the stock price could look like in the future

import yfinance as yf
from datetime import datetime, timedelta

def fetch_historical_prices(ticker: str, days: int = 30):
    """
    Fetch daily close prices for `ticker` over the last `days`.
    Returns a list of {"date": ..., "close": ...}.
    """
    end = datetime.now()
    start = end - timedelta(days=days + 1)

    df = yf.Ticker(ticker).history(
        start=start.strftime("%Y-%m-%d"),
        end=end.strftime("%Y-%m-%d"),
        interval="1d"
    )

    return [
        {"date": idx.date().isoformat(), "close": float(row["Close"])}
        for idx, row in df.iterrows()
    ]

def simulate_performance(prices, recommendation):
    if not prices or len(prices) < 2:
        return {"error": "Insufficient price data."}

    start_price = prices[0]["close"]
    end_price = prices[-1]["close"]

    dates = [p["date"] for p in prices]
    closes = [p["close"] for p in prices]

    simulated_values = []
    if recommendation.lower() == "buy":
        shares = 1 
        simulated_values = [shares * price for price in closes]
    elif recommendation.lower() == "sell":
        shares = 1
        simulated_values = [shares * (2 * start_price - price) for price in closes]
    elif recommendation.lower() == "hold":
        simulated_values = [start_price] * len(closes)
    else:
        return {"error": f"Unknown recommendation: {recommendation}"}

    return {
        "start_price": start_price,
        "end_price": end_price,
        "simulated_return_pct": ((end_price - start_price) / start_price) * 100 if recommendation.lower() == "buy"
                                 else ((start_price - end_price) / start_price) * 100 if recommendation.lower() == "sell"
                                 else 0.0,
        "graph_data": {
            "dates": dates,
            "prices": closes,
            "simulated": simulated_values
        }
    }