"""Base scraper class for event sources."""

import logging
import time
from abc import ABC, abstractmethod
from typing import Optional

import requests
from bs4 import BeautifulSoup

from ..models.event import Event

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Abstract base class for event scrapers."""

    def __init__(
        self,
        name: str,
        base_url: str,
        user_agent: str = "Mozilla/5.0 (compatible; FestCalBot/1.0)",
        delay: float = 2.0,
        max_retries: int = 3,
    ):
        self.name = name
        self.base_url = base_url
        self.user_agent = user_agent
        self.delay = delay
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})

    @abstractmethod
    def scrape(self) -> list[Event]:
        """Scrape events from the source. Must be implemented by subclasses."""
        pass

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch a page and return parsed BeautifulSoup object."""
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching {url} (attempt {attempt + 1})")
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                time.sleep(self.delay)
                return BeautifulSoup(response.text, "html.parser")
            except requests.RequestException as e:
                logger.warning(f"Failed to fetch {url}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.delay * (attempt + 1))
        return None

    def generate_event_id(self, *args) -> str:
        """Generate a unique event ID from components."""
        import hashlib
        combined = "-".join(str(arg) for arg in args)
        return hashlib.sha256(combined.encode()).hexdigest()[:16]

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name})>"
