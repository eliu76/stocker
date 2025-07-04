import os
import requests
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

def fetch_newsapi_articles(query, limit=5):
    """
    Fetch recent news from NewsAPI related to the stock.
    """
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "pageSize": limit,
        "sortBy": "publishedAt",
        "language": "en",
        "apiKey": NEWS_API_KEY
    }

    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        articles = res.json().get("articles", [])
        return [article["title"] + ". " + article.get("description", "") for article in articles]
    except Exception as e:
        return [f"[NewsAPI error] {str(e)}"]

def fetch_finnhub_news(ticker, limit=5):
    """
    Fetch company news from Finnhub related to the ticker.
    """
    url = f"https://finnhub.io/api/v1/company-news"
    params = {
        "symbol": ticker,
        "from": "2024-06-01",
        "to": "2025-07-04",
        "token": FINNHUB_API_KEY
    }

    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        articles = res.json()[:limit]
        return [a.get("headline", "") + ". " + a.get("summary", "") for a in articles]
    except Exception as e:
        return [f"[Finnhub error] {str(e)}"]

def fetch_pushshift_reddit_posts(query, limit=5):
    """
    Fetch recent Reddit comments/posts using Pushshift API (unofficial).
    """
    url = f"https://api.pushshift.io/reddit/search/comment/"
    params = {
        "q": query,
        "size": limit,
        "sort": "desc"
    }

    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        data = res.json().get("data", [])
        return [d["body"] for d in data]
    except Exception as e:
        return [f"[Reddit error] {str(e)}"]

def fetch_all_sources(ticker, name=None, limit=5):
    """
    Fetch data from NewsAPI, Finnhub, and Reddit.
    """
    name = name or ticker
    combined = []

    newsapi_articles = fetch_newsapi_articles(name, limit)
    print(f"[+] Fetched {len(newsapi_articles)} NewsAPI articles.")
    combined.extend(newsapi_articles)

    finnhub_articles = fetch_finnhub_news(ticker, limit)
    print(f"[+] Fetched {len(finnhub_articles)} Finnhub articles.")
    combined.extend(finnhub_articles)

    reddit_posts = fetch_pushshift_reddit_posts(name, limit)
    print(f"[+] Fetched {len(reddit_posts)} Reddit posts.")
    combined.extend(reddit_posts)

    return combined
