# this class loads in an Huggingface finBert model with domain-specific sentiment labels and returns a sentiment score

from transformers import pipeline
from collections import Counter
import numpy as np

# load FinBERT model
sentiment_model = pipeline("text-classification", model="ProsusAI/finbert", return_all_scores=False)

def extract_keywords(text):
    keywords = ['earnings', 'guidance', 'revenue', 'regulation', 'profit', 'loss', 'merger', 'buyback']
    matches = [word for word in keywords if word in text.lower()]
    return matches

def analyze_sentiment(texts):
    if not texts:
        return {
            "individual_scores": [],
            "average_score": 0.0,
            "overall_sentiment": "Neutral",
            "summary": "No valid input provided.",
            "distribution": {}
        }

    results = sentiment_model(texts)

    detailed_results = []
    numeric_scores = []
    label_counter = Counter()

    label_map = {
        "positive": 1,
        "neutral": 0,
        "negative": -1
    }

    for result, text in zip(results, texts):
        label = result['label'].lower()
        confidence = result['score']
        score = label_map.get(label, 0) * confidence
        numeric_scores.append(score)
        label_counter[label] += 1

        detailed_results.append({
            "text": text,
            "label": label.title(),
            "confidence": round(confidence, 4),
            "score": round(score, 4),
            "financial_keywords": extract_keywords(text),
            "financial_relevance": "High" if extract_keywords(text) else "Low"
        })

    avg_score = np.mean(numeric_scores)

    if avg_score > 0.5:
        overall = "Strongly Positive"
    elif avg_score > 0.2:
        overall = "Positive"
    elif avg_score < -0.5:
        overall = "Strongly Negative"
    elif avg_score < -0.2:
        overall = "Negative"
    else:
        overall = "Neutral"

    total = len(texts)
    dist = {
        "Positive": round(label_counter["positive"] / total * 100, 2),
        "Neutral": round(label_counter["neutral"] / total * 100, 2),
        "Negative": round(label_counter["negative"] / total * 100, 2)
    }

    summary = (
        f"{dist['Positive']}% positive, "
        f"{dist['Neutral']}% neutral, "
        f"{dist['Negative']}% negative. "
        f"Avg score: {round(avg_score, 3)}."
    )

    return {
        "individual_scores": detailed_results,
        "average_score": round(avg_score, 3),
        "overall_sentiment": overall,
        "summary": summary,
        "distribution": dist
    }
