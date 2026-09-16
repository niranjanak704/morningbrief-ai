"""
MorningBrief AI - Streamlit web app.

Run with:
    streamlit run streamlit_app.py
"""

import re
from datetime import datetime

import streamlit as st

from app.config import validate_config, BRIEFING_HOUR, BRIEFING_MINUTE, TIMEZONE
from app.main import generate_briefing, load_latest_briefing

st.set_page_config(page_title="MorningBrief AI", page_icon="📰", layout="centered")

st.title("📰 MorningBrief AI")
st.caption(
    f"Your AI-summarized morning news, sourced from The Hindu. "
    f"Automated briefings run daily at {BRIEFING_HOUR:02d}:{BRIEFING_MINUTE:02d} ({TIMEZONE})."
)

problems = validate_config()
if problems:
    st.error("Configuration problem(s) found:")
    for problem in problems:
        st.write(f"- {problem}")
    st.info("Copy `.env.example` to `.env`, fill in your Gemini API key, and restart the app.")
    st.stop()

if "briefing_text" not in st.session_state:
    st.session_state.briefing_text = load_latest_briefing()

col1, col2 = st.columns([1, 2])
with col1:
    generate_clicked = st.button("🔄 Generate Latest Briefing", type="primary", use_container_width=True)

if generate_clicked:
    with st.spinner("Fetching news from The Hindu and summarizing with Gemini... this can take a minute."):
        try:
            st.session_state.briefing_text = generate_briefing()
            st.session_state.generated_at = datetime.now().strftime("%d %b %Y, %I:%M %p")
        except Exception as exc:  # noqa: BLE001 - show the user a clean error, not a stack trace
            st.error(f"Could not generate a briefing: {exc}")

st.divider()

briefing_text = st.session_state.briefing_text

if not briefing_text:
    st.info("No briefing yet. Click **Generate Latest Briefing** above to create one.")
else:
    if "generated_at" in st.session_state:
        st.caption(f"Last generated: {st.session_state.generated_at}")

    # Split the plain-text briefing into blocks per numbered article so we
    # can render each one as a clean card with a clickable source link,
    # while still showing category headers as section dividers.
    lines = briefing_text.split("\n")

    st.markdown("## GOOD MORNING! ☀️")
    st.write("Here is your morning news briefing.")

    KNOWN_CATEGORIES = {"NATIONAL", "INTERNATIONAL", "BUSINESS", "SCI-TECH", "SPORT", "EDITORIAL", "OTHER"}
    article_pattern = re.compile(r"^\d+\.\s+(.*)")
    source_pattern = re.compile(r"^The Hindu - (.*)")

    current_headline = None
    current_state = None  # tracks which section we're reading: "what" / "why" / None
    what_lines, why_lines = [], []

    def flush_article():
        if current_headline is None:
            return
        with st.container(border=True):
            st.markdown(f"**{current_headline}**")
            if what_lines:
                st.write(" ".join(what_lines))
            if why_lines:
                st.markdown(f"*Why it matters:* {' '.join(why_lines)}")

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if line in KNOWN_CATEGORIES:
            flush_article()
            current_headline, what_lines, why_lines = None, [], []
            st.markdown(f"### {line}")
            i += 1
            continue

        match = article_pattern.match(line)
        if match:
            flush_article()
            current_headline = match.group(1)
            what_lines, why_lines = [], []
            current_state = None
            i += 1
            continue

        if line == "What happened:":
            current_state = "what"
            i += 1
            continue
        if line == "Why it matters:":
            current_state = "why"
            i += 1
            continue
        if line == "Source:":
            i += 1
            if i < len(lines):
                source_match = source_pattern.match(lines[i].strip())
                if source_match:
                    st.markdown(f"[Read full article on The Hindu ↗]({source_match.group(1)})")
            current_state = None
            i += 1
            continue

        if line and current_state == "what":
            what_lines.append(line)
        elif line and current_state == "why":
            why_lines.append(line)

        i += 1

    flush_article()

st.divider()
st.caption(
    "MorningBrief AI fetches only publicly available RSS headlines and "
    "descriptions from The Hindu, and uses Gemini strictly to summarize "
    "that text -- it does not add outside facts."
)
