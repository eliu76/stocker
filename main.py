# used for local testing

from dotenv import load_dotenv
from src.ingestion.fetch_data import fetch_all_sources, fetch_atr
from src.ingestion.parse_data import parse_input
from src.analysis.sentiment_analysis import analyze_sentiment
from src.analysis.explain_sentiment import generate_explanation
from src.analysis.generate_recommendation import generate_recommendation
from src.analysis.gpt_reccomendation import groq_recommendation_prompt
from src.ingestion.price_data import fetch_historical_prices, simulate_performance

def parse_groq_response(text):
    try:
        if "—" in text:
            parts = text.split("—", 1)
        elif "-" in text:
            parts = text.split("-", 1)
        else:
            return {"recommendation": "Hold", "reasoning": text.strip()}

        rec = parts[0].strip().capitalize()
        reason = parts[1].strip()

        if rec.lower() not in ("buy", "hold", "sell"):
            rec = "Hold"
        return {"recommendation": rec, "reasoning": reason}
    except Exception:
        return {"recommendation": "Hold", "reasoning": text.strip()}

def main():
    load_dotenv()
    ticker = "AAPL"
    name = "Apple"

    print(f"[Testing data fetch for: {ticker}]")
    raw_data = fetch_all_sources(ticker, name, limit=10)

    print("\n--- Raw Fetched Data ---")
    for line in raw_data:
        print(f"- {line}")

    cleaned = parse_input(raw_data)

    print("\n--- Parsed/Cleaned Data ---")
    for i, line in enumerate(cleaned, 1):
        print(f"{i}. {line}")

    if not cleaned:
        print("\n[!] No clean data to analyze.")
        return

    result = analyze_sentiment(cleaned)

    print("\n--- Sentiment Analysis ---")
    print(f"Overall Sentiment: {result['overall_sentiment']}")
    print(f"Average Score: {result['average_score']}")
    print(f"Summary: {result['summary']}")
    print("Distribution:", result["distribution"])

    print("\n--- Detailed Scores ---")
    for i, item in enumerate(result["individual_scores"], 1):
        print(f"{i}. [{item['label']}] ({item['score']}): {item['text']}")
        if item["financial_keywords"]:
            print(f"    ↳ Financial Keywords: {item['financial_keywords']}")

    print("\n--- Explanation ---")
    explanation = generate_explanation(result, ticker, name)
    print(explanation)

    print("\n--- Rule-Based Recommendation ---")
    rec = generate_recommendation(result, ticker, name)
    print(f"Recommendation for {rec['ticker']}: {rec['recommendation']}")
    print(f"Reasoning: {rec['reasoning']}")

    print("\n--- LLM-Based Recommendation (Groq) ---")
    atr = fetch_atr(ticker)
    volatility = "Unknown"
    if atr is not None:
        if atr < 1:
            volatility = "Low"
        elif atr <= 3:
            volatility = "Moderate"
        else:
            volatility = "High"

    raw_llm = groq_recommendation_prompt(
        avg_score=result["average_score"],
        positive_pct=result["distribution"]["Positive"],
        negative_pct=result["distribution"]["Negative"],
        neutral_pct=result["distribution"]["Neutral"],
        sentiment=result["overall_sentiment"],
        high_relevance_count=sum(1 for i in result["individual_scores"] if i["financial_relevance"] == "High"),
        atr=atr,
        volatility=volatility
    )
    parsed_llm = parse_groq_response(raw_llm)

    print(f"LLM Recommendation: {parsed_llm['recommendation']}")
    print(f"LLM Reasoning: {parsed_llm['reasoning']}")

    print("\n--- Historical Performance Simulation ---")
    prices = fetch_historical_prices(ticker, days=30)
    if not prices:
        print("[!] No historical price data available.")
        return

    sim = simulate_performance(prices, parsed_llm["recommendation"])
    print(f"Start Price: ${sim['start_price']:.2f}")
    print(f"End Price:   ${sim['end_price']:.2f}")
    print(f"Simulated Return (%): {sim['simulated_return_pct']:.2f}%")

if __name__ == "__main__":
    main()
