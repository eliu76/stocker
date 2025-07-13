from src.ingestion.fetch_data import fetch_atr

def generate_recommendation(sentiment_result, ticker, company_name=None):
    name = company_name or ticker
    avg_score = sentiment_result.get("average_score", 0.0)
    sentiment = sentiment_result.get("overall_sentiment", "Neutral")
    dist = sentiment_result.get("distribution", {})
    individual = sentiment_result.get("individual_scores", [])

    # Extract counts and proportions
    positive_pct = dist.get("Positive", 0)
    negative_pct = dist.get("Negative", 0)
    neutral_pct = dist.get("Neutral", 0)
    high_relevance_count = sum(1 for i in individual if i["financial_relevance"] == "High")
    high_confidence = sum(1 for i in individual if i["confidence"] >= 0.85)
    avg_confidence = round(sum(i["confidence"] for i in individual) / len(individual), 2) if individual else 0

    # Volatility fetch
    atr = fetch_atr(ticker)
    volatility_level = "Unknown"
    if atr is not None:
        if atr < 1:
            volatility_level = "Low"
        elif atr <= 3:
            volatility_level = "Moderate"
        else:
            volatility_level = "High"

    # Recommendation Logic
    if sentiment in ["Strongly Positive", "Positive"] and avg_score >= 0.3 and positive_pct > 50 and high_relevance_count >= 2:
        rec = "Buy"
        reason = (
            f"The sentiment surrounding {name} is {sentiment}, backed by {positive_pct:.1f}% positive coverage. "
            f"{high_relevance_count} highly relevant sources and {high_confidence} high-confidence entries suggest market optimism. "
            f"The average sentiment score is {avg_score:.2f} with an average model confidence of {avg_confidence:.2f}. "
        )
    elif sentiment in ["Strongly Negative", "Negative"] and avg_score <= -0.3 and negative_pct > 50 and high_relevance_count >= 2:
        rec = "Sell"
        reason = (
            f"Sentiment around {name} is {sentiment}, with {negative_pct:.1f}% negative coverage. "
            f"{high_relevance_count} high-relevance financial entries point to caution, supported by {high_confidence} strong-confidence flags. "
            f"The average sentiment score is {avg_score:.2f}, suggesting downside pressure."
        )
    else:
        rec = "Hold"
        reason = (
            f"The sentiment around {name} is currently {sentiment}. "
            f"{neutral_pct:.1f}% of articles are neutral, and the sentiment score of {avg_score:.2f} lacks clear conviction. "
            f"Only {high_relevance_count} sources are highly relevant, which may be insufficient for confident action. "
            f"This suggests the market is uncertain or awaiting further developments."
        )

    # Volatility adjustment
    if volatility_level != "Unknown":
        reason += f" Current volatility is {volatility_level} (ATR: {atr}). "
        if rec == "Buy" and volatility_level == "High":
            reason += "Caution is advised as price swings could lead to short-term risk despite long-term potential."
        elif rec == "Sell" and volatility_level == "Low":
            reason += "However, low volatility suggests a muted reaction in the short-term."
        elif rec == "Hold":
            reason += "This is consistent with holding, as there's no strong directional signal."

    return {
        "ticker": ticker,
        "recommendation": rec,
        "reasoning": reason
    }
