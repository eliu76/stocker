# this class creates the routes to communicate between the backend and the frontend

from flask import Blueprint, request, jsonify
from src.ingestion.fetch_data import fetch_all_sources, fetch_atr
from src.ingestion.parse_data import parse_input
from src.analysis.sentiment_analysis import analyze_sentiment
from src.analysis.explain_sentiment import generate_explanation
from src.analysis.generate_recommendation import generate_recommendation
from src.analysis.gpt_reccomendation import groq_recommendation_prompt
from src.ingestion.price_data import fetch_historical_prices, simulate_performance
from src.models.watchlist_model import Watchlist, db 
from flask import current_app

api = Blueprint("api", __name__)

def parse_groq_response(text):
    # expected format: Recommendation — Reasoning
    # returns string in JSON format
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
    
@api.route("/watchlist/performance", methods=["GET"])
def watchlist_performance():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    try:
        items = Watchlist.query.filter_by(user_id=user_id).all()
        performance_results = []

        for item in items:
            ticker = item.ticker

            prices = fetch_historical_prices(ticker, days=30)

            # Fetch recommendation using fake sentiment data or placeholder
            # Placeholder for now
            raw_llm_response = groq_recommendation_prompt(
                avg_score=0.1,  
                positive_pct=40,
                negative_pct=30,
                neutral_pct=30,
                sentiment="Neutral",
                high_relevance_count=1,
                atr=1.5,
                volatility="Moderate"
            )
            llm_rec = parse_groq_response(raw_llm_response)
            rec = llm_rec.get("recommendation", "Hold")

            sim_result = simulate_performance(prices, rec)

            performance_results.append({
                "ticker": ticker,
                "recommendation": rec,
                "performance": sim_result
            })

        return jsonify(performance_results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route("/analyze", methods=["POST"])
def analyze_stock():
    try:
        data = request.get_json(force=True)

        ticker = data.get("ticker", "").strip().upper()
        company_name = data.get("company_name", "").strip()

        if not ticker and not company_name:
            return jsonify({"error": "Please provide at least a ticker or company name."}), 400

        name_for_news = company_name or ticker
        ticker_for_finnhub = ticker or company_name[:4].upper()

        raw = fetch_all_sources(ticker_for_finnhub, name_for_news, limit=5)
        cleaned = parse_input(raw)
        sentiment_result = analyze_sentiment(cleaned)
        explanation = generate_explanation(sentiment_result, ticker_for_finnhub, name_for_news)
        recommendation = generate_recommendation(sentiment_result, ticker_for_finnhub, name_for_news)

        high_relevance_count = sum(
            1 for i in sentiment_result["individual_scores"] if i["financial_relevance"] == "High"
        )

        atr = fetch_atr(ticker_for_finnhub)
        if atr is not None:
            if atr < 1:
                volatility_level = "Low"
            elif atr <= 3:
                volatility_level = "Moderate"
            else:
                volatility_level = "High"
        else:
            volatility_level = "Unknown"

        raw_llm_response = groq_recommendation_prompt(
            avg_score=sentiment_result["average_score"],
            positive_pct=sentiment_result["distribution"]["Positive"],
            negative_pct=sentiment_result["distribution"]["Negative"],
            neutral_pct=sentiment_result["distribution"]["Neutral"],
            sentiment=sentiment_result["overall_sentiment"],
            high_relevance_count=high_relevance_count,
            atr=atr,
            volatility=volatility_level
        )
        llm_recommendation = parse_groq_response(raw_llm_response)

        historical_prices = fetch_historical_prices(ticker_for_finnhub)
        performance_simulation = simulate_performance(historical_prices, llm_recommendation["recommendation"])

        return jsonify({
            "ticker": ticker_for_finnhub,
            "company_name": name_for_news,
            "raw_sources": raw,
            "cleaned_sources": cleaned,
            "sentiment_result": sentiment_result,
            "explanation": explanation,
            "recommendation": recommendation,
            "llm_recommendation": llm_recommendation,
            "performance_simulation": performance_simulation,
            "historical_prices": historical_prices
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

