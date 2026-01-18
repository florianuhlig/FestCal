"""Tests for scraper modules."""

from src.scrapers.frankfurt_scraper import FrankfurtScraper
from src.scrapers.wiesbaden_scraper import WiesbadenScraper


class TestBaseScraper:
    """Tests for BaseScraper."""

    def test_generate_event_id(self):
        """Test event ID generation."""
        scraper = FrankfurtScraper()
        id1 = scraper.generate_event_id("title", "2024-01-01", "Frankfurt")
        id2 = scraper.generate_event_id("title", "2024-01-01", "Frankfurt")
        id3 = scraper.generate_event_id("different", "2024-01-01", "Frankfurt")

        assert id1 == id2  # Same input = same ID
        assert id1 != id3  # Different input = different ID
        assert len(id1) == 16  # ID is 16 characters


class TestFrankfurtScraper:
    """Tests for FrankfurtScraper."""

    def test_initialization(self):
        """Test scraper initialization."""
        scraper = FrankfurtScraper()
        assert scraper.name == "Frankfurt Tourismus"
        assert "frankfurt-tourismus.de" in scraper.base_url

    def test_scrape_returns_list(self):
        """Test that scrape returns a list."""
        scraper = FrankfurtScraper()
        events = scraper.scrape()
        assert isinstance(events, list)


class TestWiesbadenScraper:
    """Tests for WiesbadenScraper."""

    def test_initialization(self):
        """Test scraper initialization."""
        scraper = WiesbadenScraper()
        assert scraper.name == "Wiesbaden Marketing"
        assert "wiesbaden.de" in scraper.base_url
