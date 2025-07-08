#based on the sentiment analysis of the stock, generates a recomendation of buy, hold, or sell

from src.ingestion.fetch_data import fetch_atr

def generate_recommendation(sentiment_result, ticker, company_name=None):

    name = company_name or ticker
    avg_score = sentiment_result.get("average_score", 0.0)
    sentiment = sentiment_result.get("overall_sentiment", "Neutral")
    dist = sentiment_result.get("distribution", {})
    individual = sentiment_result.get("individual_scores", [])

    positive_pct = dist.get("Positive", 0)
    negative_pct = dist.get("Negative", 0)
    neutral_pct = dist.get("Neutral", 0)
    high_relevance_count = sum(1 for i in individual if i["financial_relevance"] == "High")

    if avg_score >= 0.5 and positive_pct > 60 and high_relevance_count >= 2:
        rec = "Buy"
        reason = (
            f"The overall sentiment for {name} is strongly positive, with {positive_pct:.1f}% of sources supporting this view. "
            f"Multiple high-relevance financial articles (≥2) mention favorable developments. This suggests strong market confidence."
        )

    elif -0.2 <= avg_score <= 0.2 or neutral_pct >= 50:
        rec = "Hold"
        reason = (
            f"Sentiment for {name} is mixed or uncertain, with {neutral_pct:.1f}% neutral coverage. "
            f"The average sentiment score of {avg_score:.2f} suggests neither strong optimism nor major concern."
        )

    elif avg_score <= -0.5 and negative_pct > 60 and high_relevance_count >= 2:
        rec = "Sell"
        reason = (
            f"Sentiment for {name} is strongly negative, with {negative_pct:.1f}% of articles expressing concern. "
            f"Several high-relevance financial sources point to potential risks. Selling may be prudent."
        )

    else:
        rec = "Hold"
        reason = (
            f"Signals for {name} are inconclusive. Sentiment does not meet the threshold for a clear Buy or Sell. "
            f"Re-evaluation after more data or events is recommended."
        )

    atr = fetch_atr(ticker)
    volatility_level = "Unknown"

    if atr is not None:
        if atr < 1:
            volatility_level = "Low"
        elif 1 <= atr <= 3:
            volatility_level = "Moderate"
        else:
            volatility_level = "High"

    # Adjust recommendation with volatility in mind:
    if rec == "Buy" and volatility_level == "High":
        reason += " However, the stock is currently highly volatile, so short-term caution may be warranted."
    elif rec == "Sell" and volatility_level == "Low":
        reason += " However, the stock's low volatility suggests market reactions may be muted."
    else:
        reason += f" Current volatility is {volatility_level} based on ATR ({atr})."

    return {
        "ticker": ticker,
        "recommendation": rec,
        "reasoning": reason
    }
