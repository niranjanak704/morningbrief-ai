"""
Uses Gemini to turn a raw article (title + description) into a short,
plain-English summary for the morning briefing.

Design choices:
- We ask Gemini to return strict JSON (response_mime_type="application/json")
  so parsing is reliable instead of scraping free-form text.
- The prompt explicitly forbids adding facts that aren't in the supplied
  title/description, and instructs Gemini to keep the original category
  when it's unsure, rather than guessing wildly.
- Every call is wrapped in error handling so that one bad Gemini response
  (network hiccup, malformed JSON, safety block, etc.) skips that single
  article instead of crashing the whole briefing.
"""

import json
from dataclasses import dataclass
from typing import Optional

from google import genai
from google.genai import types

from app.config import GEMINI_API_KEY, GEMINI_MODEL
from app.news.collector import Article

_SYSTEM_INSTRUCTION = (
    "You are a careful news editor who writes short, plain-English morning "
    "briefing entries for a general audience. You must only use "
    "information present in the article title and description you are "
    "given. Never invent facts, numbers, names, or context that are not "
    "in the source text. If the description is too thin to explain why "
    "the story matters, say so briefly rather than fabricating a reason. "
    "Always respond with a single valid JSON object and nothing else."
)

_PROMPT_TEMPLATE = """Summarize this news article for a morning briefing.

Article title: {title}
Article description: {description}
Suggested category (from the news source): {category}

Return ONLY a JSON object with exactly these keys:
- "headline": a clear, short headline (rewrite the title in simple English if needed)
- "summary": a 2-3 sentence plain-English summary of what happened, based only on the given text
- "why_it_matters": a short (1-2 sentence) explanation of why this news matters
- "category": one of NATIONAL, INTERNATIONAL, BUSINESS, SCI-TECH, SPORT, EDITORIAL, OTHER
  (use the suggested category above unless the article content clearly fits a different one)
"""


@dataclass
class SummarizedArticle:
    """A Gemini-generated summary paired with the original article's link."""
    headline: str
    summary: str
    why_it_matters: str
    category: str
    link: str


def _get_client() -> genai.Client:
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add it to your .env file before "
            "generating a briefing."
        )
    return genai.Client(api_key=GEMINI_API_KEY)


def summarize_article(client: genai.Client, article: Article) -> Optional[SummarizedArticle]:
    """
    Calls Gemini for a single article. Returns None (instead of raising)
    if the API call fails or the response can't be parsed, so the caller
    can simply skip this article and keep going.
    """
    prompt = _PROMPT_TEMPLATE.format(
        title=article.title,
        description=article.description or "(no description provided)",
        category=article.category,
    )

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=_SYSTEM_INSTRUCTION,
                temperature=0.2,
                response_mime_type="application/json",
            ),
        )
        raw_text = (response.text or "").strip()
        if not raw_text:
            print(f"[summarizer] Empty response for article: {article.title}")
            return None

        data = json.loads(raw_text)

        return SummarizedArticle(
            headline=str(data.get("headline", article.title)).strip(),
            summary=str(data.get("summary", "")).strip(),
            why_it_matters=str(data.get("why_it_matters", "")).strip(),
            category=str(data.get("category", article.category)).strip().upper(),
            link=article.link,
        )

    except json.JSONDecodeError as exc:
        print(f"[summarizer] Could not parse Gemini JSON for '{article.title}': {exc}")
        return None
    except Exception as exc:  # noqa: BLE001 - any API/network error should not crash the run
        print(f"[summarizer] Gemini API error for '{article.title}': {exc}")
        return None


def summarize_articles(articles):
    """
    Summarizes a list of Article objects, skipping any that fail.
    Returns a list of SummarizedArticle.
    """
    client = _get_client()
    summarized = []
    for article in articles:
        result = summarize_article(client, article)
        if result is not None:
            summarized.append(result)
    return summarized
