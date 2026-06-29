import httpx
import os
from dotenv import load_dotenv
load_dotenv()

url = "https://newsapi.org/v2/everything"
params = {
    "q": '"Tata Consultancy Services" OR "TCS stock news"',   # search by name not ticker
    "language": "en",
    "sortBy": "publishedAt",
    "from": "2026-06-28",             # yesterday
    "apiKey": os.getenv("NEWSAPI_KEY")
}

response = httpx.get(url, params=params)
articles = response.json()["articles"]

for article in articles:
    print(article["title"])
    print(article["description"])
    print(article["publishedAt"])
    print(article["source"]["name"])
    print("---")