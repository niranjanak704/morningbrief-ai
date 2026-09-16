"""
Cleans up raw collected articles: removes duplicates and trims each
category down to a manageable number of articles before they're sent
to Gemini for summarization.
"""

from typing import Dict, List

from app.config import MAX_ARTICLES_PER_CATEGORY
from app.news.collector import Article


def deduplicate(articles: List[Article]) -> List[Article]:
    """
    Removes duplicate articles. The Hindu sometimes syndicates the same
    story into more than one section feed, so we dedupe first by exact
    article link, then by normalized title, keeping the first occurrence
    of each.
    """
    seen_links = set()
    seen_titles = set()
    unique_articles: List[Article] = []

    for article in articles:
        link_key = article.link.strip()
        title_key = article.normalized_key()

        if link_key and link_key in seen_links:
            continue
        if title_key in seen_titles:
            continue

        seen_links.add(link_key)
        seen_titles.add(title_key)
        unique_articles.append(article)

    return unique_articles


def group_by_category(
    articles: List[Article],
    max_per_category: int = MAX_ARTICLES_PER_CATEGORY,
) -> Dict[str, List[Article]]:
    """
    Groups deduplicated articles by category and caps each category at
    `max_per_category` articles (keeping feed order, which for The Hindu's
    RSS feeds is newest-first).
    """
    grouped: Dict[str, List[Article]] = {}
    for article in articles:
        bucket = grouped.setdefault(article.category, [])
        if len(bucket) < max_per_category:
            bucket.append(article)
    return grouped


def process(articles: List[Article]) -> Dict[str, List[Article]]:
    """Full processing pipeline: deduplicate, then group and cap."""
    unique_articles = deduplicate(articles)
    print(
        f"[processor] {len(articles)} article(s) collected, "
        f"{len(unique_articles)} remain after removing duplicates"
    )
    return group_by_category(unique_articles)
