def generate_explanation(sentiment_result, ticker, company_name=None):
    """
    Converts structured sentiment analysis into a natural-language explanation.

    Parameters:
        sentiment_result (dict): Output from analyze_sentiment()
        ticker (str): Stock symbol (e.g., AAPL)
        company_name (str): Optional full name of the company (e.g., Apple)

    Returns:
        str: Narrative explanation of the sentiment findings.
    """
    name = company_name or ticker
    sentiment = sentiment_result.get("overall_sentiment", "Neutral")
    summary = sentiment_result.get("summary", "")
    dist = sentiment_result.get("distribution", {})
    detailed = sentiment_result.get("individual_scores", [])

    high_relevance = [d for d in detailed if d.get("financial_relevance") == "High"]
    low_relevance = [d for d in detailed if d.get("financial_relevance") == "Low"]

    explanation = [f"Sentiment analysis for {name} ({ticker}) reveals an **overall market tone of _{sentiment}_**."]

    if summary:
        explanation.append(summary)

    if sentiment in ["Neutral", "Negative", "Strongly Negative"]:
        explanation.append("This may reflect recent concerns, mixed outlooks, or a lack of clear catalysts.")

    if high_relevance:
        explanation.append(f"{len(high_relevance)} of the analyzed sources mentioned key financial terms such as "
                           f"{', '.join(sorted(set(k for item in high_relevance for k in item['financial_keywords'])))}.")

    if low_relevance:
        explanation.append(f"Some sources were less financially specific but still contributed to the sentiment profile.")

    if dist.get("Neutral", 0) > 40:
        explanation.append("Note that a significant portion of the content was classified as neutral, indicating possible market indecision.")

    explanation.append("These insights are based on publicly available news, social posts, and financial commentary.")
    
    return "\n".join(explanation)
