from flask import Blueprint, request, jsonify
from src.digest.daily_digest import send_email
from src.models.watchlist_model import Watchlist
from src.ingestion.price_data import fetch_historical_prices

digest_bp = Blueprint("digest", __name__)

@digest_bp.route("/send", methods=["POST"])
def send_digest():
    data = request.get_json() or {}
    user_id = data.get("user_id", "guest")
    email = data.get("email")

    if not email:
        email = "evanliu76@gmail.com"

    try:
        items = Watchlist.query.filter_by(user_id=user_id).all()
        if not items:
            return jsonify({"error": "No watchlist items found"}), 404

        digest_lines = []
        for item in items:
            prices = fetch_historical_prices(item.ticker, days=5)
            latest = prices[-1]["close"] if prices else "N/A"
            digest_lines.append(f"{item.ticker}: Latest Close ${latest}")

        digest_body = "\n".join(digest_lines)

        send_email(email, "Your Stock Watchlist Digest", f"Here is your daily watchlist update:\n\n{digest_body}")

        return jsonify({"message": "Digest sent successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
