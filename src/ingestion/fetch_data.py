# this class uses several web APIs to scrape the web for certain sentiment around an inputted stock ticker and name

import os
import requests
import praw
import time
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_SECRET = os.getenv("REDDIT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

def fetch_newsapi_articles(query, limit=5):
    """
    fetch recent news from NewsAPI related to the stock.
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
    fetch company news from Finnhub related to the ticker.
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

def fetch_reddit_posts(query, limit=5):
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )

    posts = []
    try:
        for submission in reddit.subreddit("all").search(query, limit=limit):
            posts.append(submission.title + ". " + submission.selftext[:280])
    except Exception as e:
        posts.append(f"[Reddit API error] {str(e)}")

    return posts

def fetch_all_sources(ticker, name=None, limit=5):
    """
    fetch data from NewsAPI, Finnhub, and Reddit.
    """
    name = name or ticker
    combined = []

    newsapi_articles = fetch_newsapi_articles(name, limit)
    print(f"[+] Fetched {len(newsapi_articles)} NewsAPI articles.")
    combined.extend(newsapi_articles)

    finnhub_articles = fetch_finnhub_news(ticker, limit)
    print(f"[+] Fetched {len(finnhub_articles)} Finnhub articles.")
    combined.extend(finnhub_articles)

    reddit_posts = fetch_reddit_posts(name, limit)
    print(f"[+] Fetched {len(reddit_posts)} Reddit posts.")
    combined.extend(reddit_posts)

    return combined

def fetch_atr(ticker, days=14):
    """
    Fetches Average True Range (ATR) from Finnhub — a volatility metric.
    """
    to_unix = int(time.time())
    from_unix = to_unix - 60 * 60 * 24 * (days + 20)  # 20 buffer days

    url = "https://finnhub.io/api/v1/indicator"
    params = {
        "symbol": ticker,
        "resolution": "D",
        "from": from_unix,
        "to": to_unix,
        "indicator": "atr",
        "timeperiod": days,
        "token": FINNHUB_API_KEY
    }

    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        atr_values = res.json().get("technicalAnalysis", {}).get("atr", [])
        if atr_values:
            return round(atr_values[-1], 3)  # Most recent ATR
        else:
            return None
    except Exception as e:
        print(f"[ATR fetch error] {e}")
        return None
