"""
Orchestrates the full MorningBrief AI pipeline:

    collect (RSS) -> process (dedupe/group) -> summarize (Gemini) -> format

`generate_briefing()` is the single function both the Streamlit app and
the scheduler call, so there's exactly one code path that produces a
briefing.
"""

from datetime import datetime
from typing import Dict, List

from app.news.collector import fetch_all, Article
from app.news.processor import process
from app.ai.summarizer import summarize_articles, SummarizedArticle
from app.config import DATA_DIR, LATEST_BRIEFING_PATH

import os

# Preferred display order for categories in the final briefing.
CATEGORY_ORDER = ["NATIONAL", "INTERNATIONAL", "BUSINESS", "SCI-TECH", "SPORT", "EDITORIAL", "OTHER"]


def _format_briefing(summaries_by_category: Dict[str, List[SummarizedArticle]]) -> str:
    """Builds the final plain-text briefing in the required format."""
    lines = []
    lines.append("GOOD MORNING!")
    lines.append("")
    lines.append("Here is your morning news briefing.")
    lines.append("")

    article_number = 1
    any_articles = False

    for category in CATEGORY_ORDER:
        items = summaries_by_category.get(category)
        if not items:
            continue

        any_articles = True
        lines.append(category)
        lines.append("")

        for item in items:
            lines.append(f"{article_number}. {item.headline}")
            lines.append("")
            lines.append("What happened:")
            lines.append(item.summary or "(No summary available.)")
            lines.append("")
            lines.append("Why it matters:")
            lines.append(item.why_it_matters or "(Not enough information to say.)")
            lines.append("")
            lines.append("Source:")
            lines.append(f"The Hindu - {item.link}")
            lines.append("")
            article_number += 1

    if not any_articles:
        lines.append(
            "No articles could be summarized this morning. Please check your "
            "internet connection, RSS feed URLs, and Gemini API key, then try again."
        )

    return "\n".join(lines)


def _group_summaries_by_category(summaries: List[SummarizedArticle]) -> Dict[str, List[SummarizedArticle]]:
    grouped: Dict[str, List[SummarizedArticle]] = {}
    for item in summaries:
        category = item.category if item.category in CATEGORY_ORDER else "OTHER"
        grouped.setdefault(category, []).append(item)
    return grouped


def generate_briefing(save: bool = True) -> str:
    """
    Runs the full pipeline and returns the formatted briefing text.
    If `save` is True (default), also writes it to data/latest_briefing.txt
    so the Streamlit app can display the last briefing without regenerating it.
    """
    print(f"[main] Generating briefing at {datetime.now().isoformat()}")

    raw_articles: List[Article] = fetch_all()
    grouped_articles = process(raw_articles)

    all_summaries: List[SummarizedArticle] = []
    for category, articles in grouped_articles.items():
        print(f"[main] Summarizing {len(articles)} article(s) in {category}...")
        all_summaries.extend(summarize_articles(articles))

    summaries_by_category = _group_summaries_by_category(all_summaries)
    briefing_text = _format_briefing(summaries_by_category)

    if save:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(LATEST_BRIEFING_PATH, "w", encoding="utf-8") as f:
            f.write(briefing_text)
        print(f"[main] Saved briefing to {LATEST_BRIEFING_PATH}")

    return briefing_text


def load_latest_briefing() -> str:
    """Returns the last saved briefing, or an empty string if none exists yet."""
    if os.path.exists(LATEST_BRIEFING_PATH):
        with open(LATEST_BRIEFING_PATH, "r", encoding="utf-8") as f:
            return f.read()
    return ""


if __name__ == "__main__":
    # Manual test: `python -m app.main`
    text = generate_briefing()
    print("\n" + "=" * 60)
    print(text)
