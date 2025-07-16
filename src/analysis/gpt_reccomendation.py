import os
import httpx
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama3-70b-8192"

def groq_recommendation_prompt(avg_score, positive_pct, negative_pct, neutral_pct, sentiment, high_relevance_count, atr, volatility):
    prompt = f"""
You are a financial assistant trained in sentiment-based stock analysis.

Here is the data for a stock:
- Average sentiment score: {avg_score}
- Sentiment breakdown: {positive_pct}% positive, {neutral_pct}% neutral, {negative_pct}% negative
- Overall sentiment label: {sentiment}
- Number of high-relevance financial articles: {high_relevance_count}
- Average True Range (ATR): {atr} ({volatility} volatility)

Please provide:
1. A recommendation: "Buy", "Hold", or "Sell"
2. A brief explanation (1–2 sentences) justifying the recommendation
3. Format should be Reccomendation (buy, hold, or sell) — reasoning

"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful financial assistant."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = httpx.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[Groq API Error] {str(e)}"
