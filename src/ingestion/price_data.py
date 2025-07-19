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

    if recommendation.lower() == "buy":
        return {
            "start_price": start_price,
            "end_price": end_price,
            "simulated_return_pct": ((end_price - start_price) / start_price) * 100
        }
    elif recommendation.lower() == "sell":
        return {
            "start_price": start_price,
            "end_price": end_price,
            "simulated_return_pct": ((start_price - end_price) / start_price) * 100
        }
    elif recommendation.lower() == "hold":
        return {
            "start_price": start_price,
            "end_price": end_price,
            "simulated_return_pct": 0.0
        }
    else:
        return {"error": f"Unknown recommendation: {recommendation}"}