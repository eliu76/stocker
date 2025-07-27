from flask import current_app
from src.models.watchlist_model import Watchlist, db
from src.ingestion.price_data import fetch_historical_prices, simulate_performance
from src.analysis.gpt_reccomendation import groq_recommendation_prompt
from app.routes import parse_groq_response
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import os

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

def generate_digest_for_user(user_id, user_email):
    items = Watchlist.query.filter_by(user_id=user_id).all()
    if not items:
        return None

    digest_lines = [f"📈 Watchlist Digest — {datetime.utcnow().date()}"]
    
    for item in items:
        prices = fetch_historical_prices(item.ticker, days=30)
        raw_llm_response = groq_recommendation_prompt(
            avg_score=0.1, positive_pct=40, negative_pct=30,
            neutral_pct=30, sentiment="Neutral",
            high_relevance_count=1, atr=1.5, volatility="Moderate"
        )
        rec = parse_groq_response(raw_llm_response)
        sim_result = simulate_performance(prices, rec["recommendation"])
        pct_change = sim_result.get("pct_change", "N/A")
        
        digest_lines.append(f"- {item.ticker}: {rec['recommendation']} ({pct_change}%) — {rec['reasoning']}")

    digest_content = "\n".join(digest_lines)
    send_email(user_email, "Your Daily Stock Digest", digest_content)

def send_email(to_email, subject, body):
    sender = EMAIL_USER
    password = EMAIL_PASS

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, to_email, msg.as_string())
