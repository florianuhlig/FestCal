"""Scraper for Frankfurter Stadtevents."""

import logging
import re
from datetime import datetime
from typing import Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from ..models.event import Event
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class FrankfurtScraper(BaseScraper):
    """Scraper for frankfurter-stadtevents.de events."""

    def __init__(self, fetch_details: bool = True, **kwargs):
        super().__init__(
            name="Frankfurter Stadtevents",
            base_url="https://www.frankfurter-stadtevents.de",
            **kwargs,
        )
        self.events_url = f"{self.base_url}/datum.html"
        self.fetch_details = fetch_details

    def scrape(self) -> list[Event]:
        """Scrape events from Frankfurter Stadtevents website."""
        events = []
        soup = self.fetch_page(self.events_url)

        if not soup:
            logger.error(f"Failed to fetch events page from {self.events_url}")
            return events

        event_cards = self._find_event_cards(soup)
        logger.info(f"Found {len(event_cards)} event cards on page")

        for card in event_cards:
            try:
                parsed_events = self._parse_event_card(card)
                events.extend(parsed_events)
            except Exception as e:
                logger.warning(f"Error parsing event card: {e}")
                continue

        logger.info(f"Successfully parsed {len(events)} events total")
        return events

    def _find_event_cards(self, soup: BeautifulSoup) -> list[Tag]:
        """Find event card elements in the HTML."""
        # Events are in <a> tags with hrefs containing /Datum/
        event_links = soup.find_all("a", href=re.compile(r"/Datum/\d+-\w+-\d+/"))
        return event_links

    def _parse_event_card(self, card: Tag) -> list[Event]:
        """Parse a single event card and return Event objects.

        Returns multiple Event objects if the event has multiple dates.
        """
        events = []

        # Extract URL
        url = card.get("href", "")
        if url and not url.startswith("http"):
            url = urljoin(self.base_url, url)

        # Extract title from the anchor text (excluding nested elements' text)
        title = self._extract_title(card)
        if not title:
            logger.warning(f"Could not extract title from event card: {url}")
            return events

        # Extract image URL
        img_tag = card.find("img")
        image_url = None
        if img_tag and img_tag.get("src"):
            image_url = img_tag["src"]
            if not image_url.startswith("http"):
                image_url = urljoin(self.base_url, image_url)

        # Extract dates and location from the card text
        card_text = card.get_text(separator=" ", strip=True)
        dates = self._parse_dates(card_text)
        location = self._extract_location(card_text)

        if not dates:
            logger.warning(f"No valid dates found for event: {title}")
            return events

        # Fetch additional details (price, description) from detail page
        details = {}
        if self.fetch_details and url:
            details = self._fetch_event_details(url)

        # Create an Event object for each date
        for event_date in dates:
            event_id = self.generate_event_id(title, event_date.isoformat(), self.name)

            event = Event(
                id=event_id,
                title=title,
                description=details.get("description"),
                start_datetime=event_date,
                location=location,
                city="Frankfurt am Main",
                url=url,
                image_url=image_url,
                price=details.get("price"),
                source=self.name,
            )
            events.append(event)

        return events

    def _extract_title(self, card: Tag) -> Optional[str]:
        """Extract the event title from a card element."""
        # Titles are in <h3> tags within the card
        h3_tag = card.find("h3")
        if h3_tag:
            title = h3_tag.get_text(strip=True)
            # Remove "Neu" badge text if present
            title = re.sub(r"^Neu\s+", "", title, flags=re.IGNORECASE)
            return title if title else None

        # Fallback: try to get text before "Termine in"
        text = card.get_text(separator=" ", strip=True)
        if "Termine in" in text:
            text = text.split("Termine in")[0].strip()

        # Remove "Neu" badge text if present
        text = re.sub(r"^Neu\s+", "", text, flags=re.IGNORECASE)

        # Clean up extra whitespace
        text = re.sub(r"\s+", " ", text).strip()

        return text if text else None

    def _parse_dates(self, text: str) -> list[datetime]:
        """Parse German date strings like '18.1.26' or '18.1.26 | 23.1.26'.

        Returns a list of datetime objects for each valid date found.
        """
        dates = []

        # Find date patterns: D.M.YY or DD.M.YY or D.MM.YY or DD.MM.YY
        date_pattern = r"\b(\d{1,2})\.(\d{1,2})\.(\d{2})\b"
        matches = re.findall(date_pattern, text)

        for day, month, year in matches:
            try:
                # Convert 2-digit year to 4-digit (assume 2000s)
                full_year = 2000 + int(year)
                event_date = datetime(full_year, int(month), int(day))

                # Skip dates that are clearly in the past
                if event_date >= datetime(2020, 1, 1):
                    dates.append(event_date)
            except ValueError as e:
                logger.debug(f"Invalid date {day}.{month}.{year}: {e}")
                continue

        return dates

    def _extract_location(self, text: str) -> Optional[str]:
        """Extract location from text like 'Termine in Frankfurt am Main:'."""
        match = re.search(r"Termine in ([^:]+):", text)
        if match:
            return match.group(1).strip()
        return None

    def _fetch_event_details(self, url: str) -> dict:
        """Fetch additional event details from the event detail page.

        Returns a dict with 'price', 'description', 'end_datetime' if available.
        """
        details = {}

        if not url:
            return details

        soup = self.fetch_page(url)
        if not soup:
            return details

        # Extract price from table cell - prices are in format "23 €"
        # Look for table cells containing € symbol
        for td in soup.find_all("td"):
            text = td.get_text(strip=True)
            if "€" in text:
                # Extract price pattern like "23 €" or "15,50 €"
                price_match = re.search(r"(\d+(?:[,.]\d+)?)\s*€", text)
                if price_match:
                    details["price"] = text
                    break

        # Extract description from meta tag or content
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            details["description"] = meta_desc["content"]

        return details
