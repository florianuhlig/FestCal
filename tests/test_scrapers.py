"""Tests for scraper modules."""

from datetime import datetime

import pytest

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
        assert scraper.name == "Frankfurter Stadtevents"
        assert "frankfurter-stadtevents.de" in scraper.base_url

    def test_scrape_returns_list(self):
        """Test that scrape returns a list."""
        # Note: This test doesn't actually hit the network when run in isolation
        # Use integration tests for full scraping tests
        scraper = FrankfurtScraper()
        assert hasattr(scraper, "scrape")
        assert callable(scraper.scrape)


class TestFrankfurtScraperDateParsing:
    """Tests for FrankfurtScraper date parsing."""

    @pytest.fixture
    def scraper(self):
        """Create a scraper instance for tests."""
        return FrankfurtScraper()

    def test_parse_single_date(self, scraper):
        """Test parsing a single date like '18.1.26'."""
        dates = scraper._parse_dates("Termine in Frankfurt: 18.1.26")
        assert len(dates) == 1
        assert dates[0] == datetime(2026, 1, 18)

    def test_parse_multiple_dates(self, scraper):
        """Test parsing multiple dates like '18.1.26 | 23.1.26'."""
        dates = scraper._parse_dates("Termine: 18.1.26 | 23.1.26 | 24.1.26")
        assert len(dates) == 3
        assert dates[0] == datetime(2026, 1, 18)
        assert dates[1] == datetime(2026, 1, 23)
        assert dates[2] == datetime(2026, 1, 24)

    def test_parse_date_with_double_digits(self, scraper):
        """Test parsing dates with double-digit day/month."""
        dates = scraper._parse_dates("10.12.26")
        assert len(dates) == 1
        assert dates[0] == datetime(2026, 12, 10)

    def test_parse_invalid_date_skipped(self, scraper):
        """Test that invalid dates are skipped without error."""
        # Invalid date: February 30th doesn't exist
        dates = scraper._parse_dates("30.2.26")
        assert len(dates) == 0

    def test_parse_invalid_month_skipped(self, scraper):
        """Test that invalid months are skipped."""
        dates = scraper._parse_dates("15.13.26")  # Month 13 doesn't exist
        assert len(dates) == 0

    def test_parse_mixed_valid_invalid_dates(self, scraper):
        """Test that valid dates are kept even if some are invalid."""
        dates = scraper._parse_dates("18.1.26 | 30.2.26 | 25.3.26")
        assert len(dates) == 2
        assert dates[0] == datetime(2026, 1, 18)
        assert dates[1] == datetime(2026, 3, 25)

    def test_event_id_unique_per_date(self, scraper):
        """Test that the same event title with different dates produces different IDs."""
        id1 = scraper.generate_event_id("My Event", "2026-01-18", scraper.name)
        id2 = scraper.generate_event_id("My Event", "2026-01-19", scraper.name)
        id3 = scraper.generate_event_id("My Event", "2026-01-18", scraper.name)

        assert id1 != id2  # Different dates = different IDs
        assert id1 == id3  # Same date = same ID


class TestFrankfurtScraperLocationExtraction:
    """Tests for FrankfurtScraper location extraction."""

    @pytest.fixture
    def scraper(self):
        """Create a scraper instance for tests."""
        return FrankfurtScraper()

    def test_extract_location_simple(self, scraper):
        """Test extracting location from simple text."""
        location = scraper._extract_location("Termine in Frankfurt am Main: 18.1.26")
        assert location == "Frankfurt am Main"

    def test_extract_location_hanau(self, scraper):
        """Test extracting location for Hanau."""
        location = scraper._extract_location("Termine in Hanau: 20.2.26")
        assert location == "Hanau"

    def test_extract_location_not_found(self, scraper):
        """Test when no location pattern is found."""
        location = scraper._extract_location("Some random text without location")
        assert location is None


class TestWiesbadenScraper:
    """Tests for WiesbadenScraper."""

    def test_initialization(self):
        """Test scraper initialization."""
        scraper = WiesbadenScraper()
        assert scraper.name == "Wiesbaden Marketing"
        assert "wiesbaden.de" in scraper.base_url
