import requests
from bs4 import BeautifulSoup
from logger import LOG

class HackerNewsClient:
    def __init__(self):
        self.base_url = "https://news.ycombinator.com/"

    def fetch_top_stories(self, limit=10):
        LOG.info("Fetching top stories from Hacker News...")
        try:
            response = requests.get(self.base_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            stories = []
            items = soup.select("span.titleline a")
            for item in items[:limit]:
                stories.append({
                    "title": item.text,
                    "link": item.get("href")
                })

            LOG.info(f"Fetched {len(stories)} stories from Hacker News.")
            return stories
        except Exception as e:
            LOG.error(f"Failed to fetch Hacker News stories: {e}")
            return []
