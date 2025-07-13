import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def gpt_recommendation_prompt(avg_score, positive_pct, negative_pct, neutral_pct, sentiment, high_relevance_count, atr, volatility):
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

Respond in JSON:
{{
  "recommendation": "...",
  "reason": "..."
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        return json.dumps({
            "recommendation": "Hold",
            "reason": f"GPT API error: {str(e)}"
        })
