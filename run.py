"""
MorningBrief AI - command-line entry point.

Usage:
    python run.py --now         Generate one briefing immediately and print it
    python run.py --schedule    Start the daily automation (runs forever until Ctrl+C)

If you run `python run.py` with no arguments, it defaults to --now so you
can quickly test that everything is wired up correctly.
"""

import argparse
import sys

from app.config import validate_config


def main():
    parser = argparse.ArgumentParser(description="MorningBrief AI")
    parser.add_argument(
        "--now",
        action="store_true",
        help="Generate a briefing immediately (manual test run).",
    )
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Start the daily automated scheduler (blocking).",
    )
    args = parser.parse_args()

    problems = validate_config()
    if problems:
        print("Configuration problem(s) found:")
        for problem in problems:
            print(f"  - {problem}")
        print("\nFix these in your .env file (see .env.example) and try again.")
        sys.exit(1)

    if args.schedule:
        from app.scheduler.jobs import start_scheduler
        start_scheduler()
    else:
        # Default action: generate one briefing right now.
        from app.main import generate_briefing
        briefing = generate_briefing()
        print("\n" + "=" * 60)
        print(briefing)
        print("=" * 60)
        print("\nBriefing generated. Run 'python run.py --schedule' to "
              "automate this every morning, or 'streamlit run streamlit_app.py' "
              "to use the web interface.")


if __name__ == "__main__":
    main()
