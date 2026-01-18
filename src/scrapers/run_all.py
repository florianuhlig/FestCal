"""Run all enabled scrapers."""

import argparse
import logging
from datetime import datetime

import yaml

from ..database.db_handler import DatabaseHandler
from ..utils.deduplicator import Deduplicator
from .frankfurt_scraper import FrankfurtScraper
from .wiesbaden_scraper import WiesbadenScraper
from .tourismus_scraper import TourismusScraper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

SCRAPER_MAP = {
    "frankfurt_scraper": FrankfurtScraper,
    "wiesbaden_scraper": WiesbadenScraper,
    "tourismus_scraper": TourismusScraper,
}


def load_sources(config_path: str = "config/sources.yaml") -> list[dict]:
    """Load source configuration."""
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config.get("sources", [])


def run_all_scrapers(sources_path: str = "config/sources.yaml") -> int:
    """Run all enabled scrapers and store events. Returns total event count."""
    sources = load_sources(sources_path)
    db_handler = DatabaseHandler()
    db_handler.init_db()
    deduplicator = Deduplicator()

    all_events = []

    for source in sources:
        if not source.get("enabled", False):
            logger.info(f"Skipping disabled source: {source['name']}")
            continue

        scraper_name = source.get("scraper")
        if scraper_name not in SCRAPER_MAP:
            logger.warning(f"Unknown scraper: {scraper_name}")
            continue

        try:
            scraper_class = SCRAPER_MAP[scraper_name]
            if scraper_name == "tourismus_scraper":
                scraper = scraper_class(name=source["name"], base_url=source["url"])
            else:
                scraper = scraper_class()

            logger.info(f"Running scraper: {source['name']}")
            events = scraper.scrape()
            logger.info(f"Found {len(events)} events from {source['name']}")
            all_events.extend(events)

        except Exception as e:
            logger.error(f"Error running scraper {source['name']}: {e}")

    # Deduplicate events
    unique_events = deduplicator.deduplicate(all_events)
    logger.info(f"After deduplication: {len(unique_events)} unique events")

    # Store in database
    added = db_handler.add_events(unique_events)
    logger.info(f"Added {added} new events to database")

    return len(unique_events)


def main():
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Run event scrapers")
    parser.add_argument(
        "--sources",
        default="config/sources.yaml",
        help="Path to sources configuration file",
    )
    args = parser.parse_args()

    total = run_all_scrapers(args.sources)
    print(f"Scraping complete. Total events: {total}")


if __name__ == "__main__":
    main()
