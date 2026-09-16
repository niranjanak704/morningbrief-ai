"""
Automation for MorningBrief AI using APScheduler.

`start_scheduler()` runs `generate_briefing()` automatically every morning
at BRIEFING_HOUR:BRIEFING_MINUTE (from .env), and keeps running in the
foreground (blocking) so it can be launched with a simple
`python run.py --schedule` and left running in a terminal.
"""

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import BRIEFING_HOUR, BRIEFING_MINUTE, TIMEZONE
from app.main import generate_briefing


def _run_job():
    try:
        generate_briefing()
        print("[scheduler] Briefing generated successfully.")
    except Exception as exc:  # noqa: BLE001 - a failed run should not kill the scheduler
        print(f"[scheduler] Briefing generation failed: {exc}")


def start_scheduler():
    """
    Starts a blocking scheduler that triggers the briefing job daily at
    the configured hour/minute, in the configured timezone. This call
    does not return until the process is interrupted (Ctrl+C).
    """
    scheduler = BlockingScheduler(timezone=TIMEZONE)
    scheduler.add_job(
        _run_job,
        trigger=CronTrigger(hour=BRIEFING_HOUR, minute=BRIEFING_MINUTE),
        id="daily_morning_briefing",
        name="Daily MorningBrief AI generation",
        misfire_grace_time=3600,  # allow up to 1 hour of delay (e.g. laptop was asleep)
    )

    print(
        f"[scheduler] MorningBrief AI automation started. Briefing will run "
        f"daily at {BRIEFING_HOUR:02d}:{BRIEFING_MINUTE:02d} ({TIMEZONE}). "
        f"Press Ctrl+C to stop."
    )

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n[scheduler] Stopped.")


if __name__ == "__main__":
    # Manual test: `python -m app.scheduler.jobs`
    start_scheduler()
