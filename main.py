from dotenv import load_dotenv
from src.ingestion.fetch_data import fetch_all_sources
from src.ingestion.parse_data import parse_input

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

if __name__ == "__main__":
    main()
