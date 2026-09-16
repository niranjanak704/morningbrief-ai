"""
Fetches raw articles from The Hindu's RSS feeds using feedparser.

This module ONLY collects data -- it does not summarize or judge
importance. That keeps it easy to test and easy to swap RSS sources
without touching any AI code.
"""

from dataclasses import dataclass, field
from typing import List, Optional
import time

import feedparser

from app.news.rss_sources import RSS_FEEDS


@dataclass
class Article:
    """A single news article collected from an RSS feed."""
    title: str
    description: str
    link: str
    published: str
    category: str

    def normalized_key(self) -> str:
        """
        A loose fingerprint used for duplicate detection: lowercase title
        with extra whitespace collapsed. Two articles about the same story
        (even syndicated with slightly different casing) will usually
        share this key.
        """
        return " ".join(self.title.lower().split())


def _safe_get(entry, field_name: str, default: str = "") -> str:
    """feedparser entries don't always have every field -- fetch safely."""
    value = entry.get(field_name, default)
    return value if isinstance(value, str) else default


def fetch_category(category: str, feed_url: str, retries: int = 2) -> List[Article]:
    """
    Fetch and parse a single RSS feed. Returns an empty list (never raises)
    if the feed is unreachable or malformed, so one bad feed can't crash
    the whole briefing.
    """
    last_error: Optional[Exception] = None

    for attempt in range(1, retries + 1):
        try:
            parsed = feedparser.parse(feed_url)

            # feedparser sets `bozo=1` when the feed XML was malformed.
            # It can still contain usable entries, so we only treat it as
            # a hard failure when there are ALSO no entries.
            if parsed.bozo and not parsed.entries:
                raise ValueError(
                    f"Feed for {category} looks malformed and had no "
                    f"entries (bozo_exception={parsed.get('bozo_exception')})"
                )

            articles = []
            for entry in parsed.entries:
                articles.append(
                    Article(
                        title=_safe_get(entry, "title", "(untitled)"),
                        description=_safe_get(entry, "summary", ""),
                        link=_safe_get(entry, "link", ""),
                        published=_safe_get(entry, "published", ""),
                        category=category,
                    )
                )
            return articles

        except Exception as exc:  # noqa: BLE001 - we want to catch and retry any parse/network issue
            last_error = exc
            if attempt < retries:
                time.sleep(1.5)  # brief backoff before retrying
            continue

    print(f"[collector] Failed to fetch '{category}' from {feed_url}: {last_error}")
    return []


def fetch_all() -> List[Article]:
    """Fetch articles from every configured RSS feed."""
    all_articles: List[Article] = []
    for category, feed_url in RSS_FEEDS.items():
        articles = fetch_category(category, feed_url)
        print(f"[collector] {category}: fetched {len(articles)} article(s)")
        all_articles.extend(articles)
    return all_articles


if __name__ == "__main__":
    # Quick manual test: `python -m app.news.collector`
    # Run this after setting up your .env to confirm every RSS feed in
    # rss_sources.py is reachable and returning articles.
    results = fetch_all()
    print(f"\nTotal articles fetched: {len(results)}")
    for article in results[:5]:
        print(f"- [{article.category}] {article.title} -> {article.link}")
