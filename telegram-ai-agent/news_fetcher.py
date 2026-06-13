import asyncio
import aiohttp
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from config import RSS_FEEDS

DEFAULT_EDUCATION_FEEDS = [
    "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "https://rss.cnn.com/rss/edition_technology.rss",
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
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    return []
                text = await resp.text()

        root = ET.fromstring(text)
        channel = root.find("channel")
        if channel is None:
            return []

        source = channel.findtext("title", url)

        for item in channel.findall("item")[:5]:
            title = item.findtext("title", "").strip()
            summary = item.findtext("description", "").strip()
            link = item.findtext("link", "").strip()

            # HTML teglarini tozalash
            import re
            summary = re.sub(r"<[^>]+>", "", summary)[:400]

            if title:
                items.append(NewsItem(title=title, summary=summary, url=link, source=source))
    except Exception as e:
        print(f"RSS xatosi ({url}): {e}")
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
