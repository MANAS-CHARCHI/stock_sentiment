import httpx
import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
load_dotenv()

url = "https://newsapi.org/v2/everything"
params = {
    "q": '"Tata Consultancy Services" OR "TCS stock news"',
    "language": "en",
    "sortBy": "publishedAt",
    "apiKey": os.getenv("NEWSAPI_KEY")
}

response = httpx.get(url, params=params)
articles = response.json()["articles"]
cutoff = datetime.now(timezone.utc) - timedelta(days=5)
for article in articles[:5]:
    published_at = datetime.fromisoformat(
        article["publishedAt"].replace("Z", "+00:00")
    )
    if published_at > cutoff:
        print(article["title"])
        print(article["description"])
        print(article["publishedAt"])
        print(article["source"]["name"])
        print("---")