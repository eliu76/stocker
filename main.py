from dotenv import load_dotenv
from src.ingestion.fetch_data import fetch_all_sources
from src.ingestion.parse_data import parse_input
from src.analysis.sentiment_analysis import analyze_sentiment
from src.analysis.explain_sentiment import generate_explanation
from src.analysis.generate_recommendation import generate_recommendation


def main():
    load_dotenv()
    ticker = "AAPL"
    name = "Apple"

    print(f"[Testing data fetch for: {ticker}]")
    raw_data = fetch_all_sources(ticker, name, limit=5)

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

    print("\n--- Recommendation ---")
    rec = generate_recommendation(result, ticker, name)
    print(f"Recommendation for {rec['ticker']}: {rec['recommendation']}")
    print(f"Reasoning: {rec['reasoning']}")

if __name__ == "__main__":
    main()
