from flask import Blueprint, request, jsonify
from src.ingestion.fetch_data import fetch_all_sources
from src.ingestion.parse_data import parse_input
from src.analysis.sentiment_analysis import analyze_sentiment
from src.analysis.explain_sentiment import generate_explanation
from src.analysis.generate_recommendation import generate_recommendation

api = Blueprint("api", __name__)

@api.route("/analyze", methods=["POST"])
def analyze_stock():
    try:
        data = request.get_json(force=True)

        ticker = data.get("ticker", "").strip().upper()
        company_name = data.get("company_name", "").strip()

        # Require at least one identifier
        if not ticker and not company_name:
            return jsonify({"error": "Please provide at least a ticker or company name."}), 400

        name_for_news = company_name or ticker
        ticker_for_finnhub = ticker or company_name[:4].upper()

        # Fetch and process data
        raw = fetch_all_sources(ticker_for_finnhub, name_for_news, limit=5)
        cleaned = parse_input(raw)
        sentiment_result = analyze_sentiment(cleaned)
        explanation = generate_explanation(sentiment_result, ticker_for_finnhub, name_for_news)
        recommendation = generate_recommendation(sentiment_result, ticker_for_finnhub, name_for_news)

        return jsonify({
            "ticker": ticker_for_finnhub,
            "company_name": name_for_news,
            "raw_sources": raw,
            "cleaned_sources": cleaned,
            "sentiment_result": sentiment_result,
            "explanation": explanation,
            "recommendation": recommendation
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
