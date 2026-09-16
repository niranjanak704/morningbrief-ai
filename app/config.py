"""
Central configuration for MorningBrief AI.

All settings come from environment variables (loaded from a local .env
file via python-dotenv). Nothing here is hardcoded -- especially not the
Gemini API key.
"""

import os
from dotenv import load_dotenv

# Load variables from a .env file in the project root, if present.
load_dotenv()


def _get_int(name: str, default: int) -> int:
    """Read an environment variable as an int, falling back safely."""
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError:
        print(f"[config] Warning: {name}='{raw}' is not a valid integer. "
              f"Using default {default}.")
        return default


# ---- Gemini API settings -------------------------------------------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# gemini-2.5-flash is the current stable, free-tier-friendly model as of
# when this project was built. Google has announced that the Gemini 2.5
# family is scheduled to be retired around October 16, 2026. If your
# requests start failing after that date, change GEMINI_MODEL in your
# .env file to whatever the current stable "flash" model is at
# https://ai.google.dev/gemini-api/docs/models -- no code changes needed.
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# ---- Scheduling settings --------------------------------------------------

BRIEFING_HOUR = _get_int("BRIEFING_HOUR", 8)
BRIEFING_MINUTE = _get_int("BRIEFING_MINUTE", 0)
TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")

# ---- News collection settings ---------------------------------------------

# Maximum number of articles to summarize per category, per run.
# Kept small on purpose to control Gemini API usage/costs.
MAX_ARTICLES_PER_CATEGORY = _get_int("MAX_ARTICLES_PER_CATEGORY", 3)

# Where the most recently generated briefing is cached as plain text,
# so the Streamlit app can show the last briefing without regenerating it.
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
LATEST_BRIEFING_PATH = os.path.join(DATA_DIR, "latest_briefing.txt")


def validate_config():
    """
    Basic sanity checks. Called by entry points (run.py, streamlit_app.py)
    so failures are reported clearly instead of as a confusing traceback
    deep inside the Gemini client.
    """
    problems = []
    if not GEMINI_API_KEY:
        problems.append(
            "GEMINI_API_KEY is not set. Copy .env.example to .env and add "
            "your Gemini API key."
        )
    if not (0 <= BRIEFING_HOUR <= 23):
        problems.append("BRIEFING_HOUR must be between 0 and 23.")
    if not (0 <= BRIEFING_MINUTE <= 59):
        problems.append("BRIEFING_MINUTE must be between 0 and 59.")
    return problems
