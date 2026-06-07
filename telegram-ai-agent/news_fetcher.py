import feedparser
import aiohttp
import asyncio
from dataclasses import dataclass
from config import RSS_FEEDS, CHANNEL_TOPIC

DEFAULT_EDUCATION_FEEDS = [
    "https://feeds.feedburner.com/TedTalks_video",
    "https://www.edx.org/feed",
    "https://rss.coursera.org/blog",
]


@dataclass
class NewsItem:
    title: str
    summary: str
    url: str
    source: str


async def fetch_rss_feed(url: str) -> list[NewsItem]:
    items = []
    try:
        loop = asyncio.get_event_loop()
        feed = await loop.run_in_executor(None, feedparser.parse, url)
        source = feed.feed.get("title", url)

        for entry in feed.entries[:5]:
            title = entry.get("title", "")
            summary = entry.get("summary", entry.get("description", ""))
            link = entry.get("link", "")

            if len(summary) > 500:
                summary = summary[:500] + "..."

            if title:
                items.append(NewsItem(
                    title=title,
                    summary=summary,
                    url=link,
                    source=source,
                ))
    except Exception as e:
        print(f"RSS feed xatosi ({url}): {e}")
    return items


async def fetch_all_news() -> list[NewsItem]:
    feeds = RSS_FEEDS if RSS_FEEDS else DEFAULT_EDUCATION_FEEDS
    tasks = [fetch_rss_feed(url) for url in feeds]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_items = []
    for result in results:
        if isinstance(result, list):
            all_items.extend(result)
    return all_items


async def get_latest_news(limit: int = 5) -> list[NewsItem]:
    items = await fetch_all_news()
    return items[:limit]
