import os
from dotenv import load_dotenv
from src.ingestion.fetch_data import fetch_all_sources

def main():
    load_dotenv()  # Load API keys from .env

    ticker = "AAPL"
    name = "Apple"

    print(f"\n[Testing data fetch for: {ticker} - {name}]")

    results = fetch_all_sources(ticker=ticker, name=name, limit=3)

    print("\n--- Combined Fetched Data ---\n")
    for i, content in enumerate(results, 1):
        print(f"{i}. {content}\n")

if __name__ == "__main__":
    main()
