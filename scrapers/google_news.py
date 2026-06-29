import feedparser
from gnews import GNews
from urllib.parse import quote
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime


def get_stock_news(company_name: str, days: int = 7):
    google_news = GNews(
        language="en",
        country="IN",
        period=f"{days}d",
        max_results=5
    )

    results = google_news.get_news(f"{company_name} stock")

    cutoff = datetime.now(tz=datetime.now().astimezone().tzinfo) - timedelta(days=days)

    articles = []
    for item in results:
        try:
            published = datetime.strptime(
                item["published date"], "%a, %d %b %Y %H:%M:%S %Z"
            ).replace(tzinfo=datetime.now().astimezone().tzinfo)

            if published >= cutoff:
                articles.append({
                    "title": item["title"],
                    "published": item["published date"],
                    "summary": item.get("description", ""),
                    "source": item.get("publisher", {}).get("title", "")
                })
        except Exception:
            continue

    return articles


articles = get_stock_news("Persistent Systems", days=1)
print(f"Found {len(articles)} articles")
for a in articles:
    print(a["title"])
    print(a["source"])
    print(a["published"])
    print("---")