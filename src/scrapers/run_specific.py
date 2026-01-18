"""Run a specific scraper by name."""

import argparse
import logging

import yaml

from ..database.db_handler import DatabaseHandler
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


def run_specific_scraper(source_name: str, sources_path: str = "config/sources.yaml") -> int:
    """Run a specific scraper by source name. Returns event count."""
    sources = load_sources(sources_path)
    db_handler = DatabaseHandler()
    db_handler.init_db()

    source = None
    for s in sources:
        if s["name"] == source_name:
            source = s
            break

    if not source:
        logger.error(f"Source not found: {source_name}")
        return 0

    scraper_name = source.get("scraper")
    if scraper_name not in SCRAPER_MAP:
        logger.error(f"Unknown scraper: {scraper_name}")
        return 0

    try:
        scraper_class = SCRAPER_MAP[scraper_name]
        if scraper_name == "tourismus_scraper":
            scraper = scraper_class(name=source["name"], base_url=source["url"])
        else:
            scraper = scraper_class()

        logger.info(f"Running scraper: {source_name}")
        events = scraper.scrape()
        logger.info(f"Found {len(events)} events")

        added = db_handler.add_events(events)
        logger.info(f"Added {added} new events to database")

        return len(events)

    except Exception as e:
        logger.error(f"Error running scraper: {e}")
        return 0


def main():
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Run a specific scraper")
    parser.add_argument("--source", required=True, help="Source name to run")
    parser.add_argument(
        "--sources-file",
        default="config/sources.yaml",
        help="Path to sources configuration file",
    )
    args = parser.parse_args()

    total = run_specific_scraper(args.source, args.sources_file)
    print(f"Scraping complete. Events found: {total}")


if __name__ == "__main__":
    main()
