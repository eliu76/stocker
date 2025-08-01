# this class uses several web APIs to scrape the web for certain sentiment around an inputted stock ticker and name

import os
import requests
import praw
import time
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_SECRET = os.getenv("REDDIT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

def fetch_newsapi_articles(query, limit=10):

    finance_keywords = "(stock OR market OR earnings OR finance OR investment OR analyst)"
    combined_query = f"{query} OR {finance_keywords}"

    trusted_sources = "bloomberg,reuters,cnbc,the-wall-street-journal,financial-times"

    from_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": combined_query,
        "pageSize": limit,
        "sortBy": "relevancy",
        "language": "en",
        "sources": trusted_sources,
        "from": from_date,
        "apiKey": NEWS_API_KEY
    }

    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        articles = res.json().get("articles", [])
        return [article["title"] + ". " + article.get("description", "") for article in articles]
    except Exception as e:
        return [f"[NewsAPI error] {str(e)}"]

def fetch_finnhub_news(ticker, limit=10):
    """
    fetch company news from Finnhub and filter for finance-related articles.
    """
    url = f"https://finnhub.io/api/v1/company-news"
    params = {
        "symbol": ticker,
        "from": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
        "to": datetime.now().strftime("%Y-%m-%d"),
        "token": FINNHUB_API_KEY
    }

    finance_keywords = {"stock", "market", "earnings", "finance", "investment", "analyst"}

    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        articles = res.json()

        filtered = []
        for a in articles:
            headline = a.get("headline", "").lower()
            summary = a.get("summary", "").lower()

            if any(kw in headline or kw in summary for kw in finance_keywords):
                filtered.append(a)

            if len(filtered) >= limit:
                break

        return [f"{a.get('headline', '')}. {a.get('summary', '')}" for a in filtered]

    except Exception as e:
        return [f"[Finnhub error] {str(e)}"]

def fetch_reddit_posts(query, limit=10):
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )

    posts = []
    subreddits = ["investing", "stocks", "finance", "ValueInvesting"]
    per_sub_limit = max(1, limit // len(subreddits))

    try:
        for subreddit_name in subreddits:
            for submission in reddit.subreddit(subreddit_name).search(query, limit=per_sub_limit):
                post_text = submission.title + ". " + (submission.selftext[:280] if submission.selftext else "")
                posts.append(post_text)
    except Exception as e:
        posts.append(f"[Reddit API error] {str(e)}")

    return posts

def fetch_all_sources(ticker, name=None, limit=10):
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
    from_unix = to_unix - 60 * 60 * 24 * (days + 20)

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
            return round(atr_values[-1], 3)
        else:
            return None
    except Exception as e:
        print(f"[ATR fetch error] {e}")
        return None
