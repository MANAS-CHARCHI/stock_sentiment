import httpx

url = "https://news.google.com/rss/articles/CBMirAFBVV95cUxPVzRwVjlvTU5zejh2ZlB6cFFsWjBTamVHNjByOVVjOTdmd0x6UkM2X19ZZlI0VTJndmtVakozd3BVeXBTYTN2MVpfWlk0WjZuNmJrRVVwLU1pV0NIZGxFTldFWjFjenNvWEp3ZWFQWUMxQ1NmTmxhT3lVOEJDWDlTUUVuaEFQQS1vOUNzTkFISUJXbHUzRmpyanlHV0hyczVJRkpJMGJLaHB1cVdM?oc=5&hl=en-IN&gl=IN&ceid=IN:en"

response = httpx.get(url, follow_redirects=True)
print(response.status_code)
print(response.url)