"""
TikTok Live Center → Google Sheets automation.

Usage:
    # Run once (scrape yesterday's sessions and write to Sheets)
    python main.py

    # Run for a specific date
    python main.py --date 2026-03-09

    # Start the daily scheduler (runs every day at SCHEDULE_TIME from .env)
    python main.py --scheduler
"""

import argparse
import logging
import sys
from datetime import date, timedelta

import schedule
import time

from config import SCHEDULE_TIME
from scraper import scrape_sessions_by_date
from sheets import append_sessions

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("tiktok_live_tracker.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


def run_for_date(target: date) -> None:
    logger.info("=== Scraping sessions for %s ===", target.isoformat())
    sessions = scrape_sessions_by_date(target)

    if not sessions:
        logger.info("No LIVE sessions found for %s.", target.isoformat())
        return

    logger.info("Found %d session(s). Writing to Google Sheets...", len(sessions))
    written = append_sessions(sessions)
    logger.info("Done. %d row(s) written.", written)


def daily_job() -> None:
    """Job executed by the scheduler: scrape yesterday's data."""
    yesterday = date.today() - timedelta(days=1)
    try:
        run_for_date(yesterday)
    except Exception as e:
        logger.error("Daily job failed: %s", e, exc_info=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="TikTok Live data → Google Sheets")
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Target date in YYYY-MM-DD format (default: yesterday)",
    )
    parser.add_argument(
        "--scheduler",
        action="store_true",
        help="Start the daily scheduler instead of a one-shot run",
    )
    args = parser.parse_args()

    if args.scheduler:
        logger.info("Scheduler started. Running daily at %s.", SCHEDULE_TIME)
        schedule.every().day.at(SCHEDULE_TIME).do(daily_job)
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        if args.date:
            target = date.fromisoformat(args.date)
        else:
            target = date.today() - timedelta(days=1)
        run_for_date(target)


if __name__ == "__main__":
    main()
