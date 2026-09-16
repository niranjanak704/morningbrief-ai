# MorningBrief AI

An AI-powered morning news briefing generator. It pulls the latest
headlines from **The Hindu's RSS feeds**, summarizes each story in
simple English with **Gemini**, explains why it matters, organizes
everything by category, and shows it in a clean **Streamlit** web app.
A briefing can also be generated automatically every morning using
**APScheduler**.

No database, no Telegram bot, no Docker, no paid cloud services --
just Python.

---

## Project Structure

```text
morningbrief-ai/
├── app/
│   ├── main.py                 # Orchestrates the full pipeline
│   ├── config.py                # Loads settings from .env
│   ├── news/
│   │   ├── collector.py         # Fetches RSS feeds
│   │   ├── processor.py         # Deduplicates & groups articles
│   │   └── rss_sources.py       # The Hindu RSS feed URLs (edit here if a feed changes)
│   ├── ai/
│   │   └── summarizer.py        # Calls Gemini to summarize each article
│   └── scheduler/
│       └── jobs.py              # APScheduler daily automation
├── streamlit_app.py             # Web interface
├── run.py                       # Command-line entry point
├── requirements.txt
├── .env.example
└── data/                        # Stores the most recently generated briefing
```

---

## 1. Installing Python

You need **Python 3.10 or newer**.

1. Go to [python.org/downloads](https://www.python.org/downloads/).
2. Download the latest Windows installer.
3. Run it, and on the first screen **check the box "Add python.exe to PATH"** before clicking Install.
4. To confirm it worked, open **Command Prompt** and run:
   ```
   python --version
   ```
   You should see something like `Python 3.12.x`.

---

## 2. Creating and activating a virtual environment (Windows)

Open Command Prompt in the project folder (the folder containing this
README) and run:

```
python -m venv venv
venv\Scripts\activate
```

Your prompt should now start with `(venv)`. Do this every time before
working on the project. To deactivate later, just type `deactivate`.

> Using PowerShell instead of Command Prompt? Use:
> `venv\Scripts\Activate.ps1`
> (If you get a script-execution error, run PowerShell as Administrator
> and execute `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once.)

---

## 3. Installing dependencies

With your virtual environment active:

```
pip install -r requirements.txt
```

---

## 4. Creating a Gemini API key

1. Go to [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey).
2. Sign in with a Google account.
3. Click **Create API key** and copy the key it gives you.
4. Keep it private -- treat it like a password.

---

## 5. Creating the `.env` file

1. In the project folder, copy `.env.example` to a new file named `.env`.
   - In Command Prompt: `copy .env.example .env`
2. Open `.env` in a text editor and paste your Gemini key:
   ```
   GEMINI_API_KEY=paste_your_real_key_here
   ```
3. Optionally adjust `BRIEFING_HOUR`, `BRIEFING_MINUTE`, `TIMEZONE`, and
   `MAX_ARTICLES_PER_CATEGORY` to your liking.
4. **Never commit or share your `.env` file** -- `.gitignore` already
   excludes it.

---

## 6. Running the Streamlit application

```
streamlit run streamlit_app.py
```

This opens a browser tab at `http://localhost:8501`. Click **Generate
Latest Briefing** to fetch, summarize, and display today's news.

---

## 7. Running the scheduled automation

To have a briefing generated automatically every morning at the time
set in `.env`:

```
python run.py --schedule
```

Leave this running in a terminal window (or set it up as a Windows
Scheduled Task pointing at this command if you want it to survive
reboots). Press `Ctrl+C` to stop it.

Each automated run overwrites `data/latest_briefing.txt`, which the
Streamlit app reads on startup -- so you can open the web app any time
after a scheduled run to see the latest briefing without waiting.

---

## 8. Testing the application manually

To generate one briefing immediately and print it to the console
(without waiting for the schedule or opening Streamlit):

```
python run.py --now
```

or simply:

```
python run.py
```

To test only the RSS collection step (useful if you suspect a feed URL
has changed):

```
python -m app.news.collector
```

---

## 9. Troubleshooting common errors

**`GEMINI_API_KEY is not set`**
You haven't created `.env` yet, or it's missing the key. See step 5.

**`ModuleNotFoundError: No module named 'app'`**
Run commands from the project's root folder (the one containing
`run.py`), not from inside `app/`.

**A category shows 0 articles / "Failed to fetch" in the console**
The Hindu occasionally reorganizes its RSS URLs. Open
`app/news/rss_sources.py`, visit the matching section on
[thehindu.com](https://www.thehindu.com) in your browser, and update
that one URL. Run `python -m app.news.collector` to confirm it's fixed.

**`Gemini API error` in the console for some articles**
This is usually a temporary network issue, rate limit, or an invalid
API key. Those articles are simply skipped; the rest of the briefing
still generates. If it happens for every article, double-check your
API key and your internet connection.

**Summaries stop working entirely after October 2026**
Google has scheduled the Gemini 2.5 model family for retirement around
October 16, 2026. Open `.env` and change `GEMINI_MODEL` to the current
stable "flash" model name listed at
[ai.google.dev/gemini-api/docs/models](https://ai.google.dev/gemini-api/docs/models).
No code changes are needed.

**Streamlit opens but shows a configuration error**
Check the exact message on-screen -- it lists exactly which `.env`
setting is missing or invalid.

**PowerShell won't let me activate the virtual environment**
See the note at the end of step 2 about `Set-ExecutionPolicy`.

---

## Notes on data & privacy

- No database is used. The only file the app writes is
  `data/latest_briefing.txt`, a plain text cache of the most recent
  briefing.
- The Gemini prompt explicitly instructs the model not to add facts
  beyond what's in each article's RSS title/description, and every
  summary keeps a link back to the original article on The Hindu.
