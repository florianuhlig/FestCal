"""Integration tests for scrapers with mocked HTTP responses."""

from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.scrapers.frankfurt_scraper import FrankfurtScraper


class TestFrankfurtScraperIntegration:
    """Integration tests for FrankfurtScraper with mocked HTTP."""

    @pytest.fixture
    def sample_html(self):
        """Load sample HTML fixture."""
        fixture_path = Path(__file__).parent / "fixtures" / "frankfurt_events_page.html"
        return fixture_path.read_text(encoding="utf-8")

    @pytest.fixture
    def scraper(self):
        """Create a scraper instance with mocked session."""
        return FrankfurtScraper()

    def test_scrape_with_mocked_response(self, scraper, sample_html):
        """Test full scrape() method with mocked HTTP response."""
        mock_response = MagicMock()
        mock_response.text = sample_html
        mock_response.raise_for_status = MagicMock()

        with patch.object(scraper.session, "get", return_value=mock_response):
            events = scraper.scrape()

        # Should find multiple events (multi-date events create separate entries)
        assert len(events) > 0

        # Check first event properties
        first_event = events[0]
        assert first_event.title is not None
        assert first_event.start_datetime is not None
        assert first_event.source == "Frankfurter Stadtevents"
        assert first_event.id is not None

    def test_scrape_extracts_all_events(self, scraper, sample_html):
        """Test that all events are extracted from the page."""
        mock_response = MagicMock()
        mock_response.text = sample_html
        mock_response.raise_for_status = MagicMock()

        with patch.object(scraper.session, "get", return_value=mock_response):
            events = scraper.scrape()

        # Count expected events:
        # Event 1: 1 date = 1 event
        # Event 2: 3 dates = 3 events
        # Event 3: 2 dates = 2 events
        # Event 4: 1 date = 1 event
        # Event 5: 3 dates = 3 events
        # Total: 10 events
        assert len(events) == 10

    def test_scrape_extracts_correct_titles(self, scraper, sample_html):
        """Test that event titles are correctly extracted."""
        mock_response = MagicMock()
        mock_response.text = sample_html
        mock_response.raise_for_status = MagicMock()

        with patch.object(scraper.session, "get", return_value=mock_response):
            events = scraper.scrape()

        titles = {e.title for e in events}
        assert "Entdecke Frankfurt - Zwischen Mainufer & Altstadtflair" in titles
        assert "Jazz im Palmengarten" in titles
        assert "Hanauer Kulturabend" in titles

    def test_scrape_extracts_correct_dates(self, scraper, sample_html):
        """Test that event dates are correctly extracted."""
        mock_response = MagicMock()
        mock_response.text = sample_html
        mock_response.raise_for_status = MagicMock()

        with patch.object(scraper.session, "get", return_value=mock_response):
            events = scraper.scrape()

        # Filter events for "Jazz im Palmengarten" which has 3 dates
        jazz_events = [e for e in events if "Jazz" in e.title]
        assert len(jazz_events) == 3

        jazz_dates = sorted([e.start_datetime for e in jazz_events])
        assert jazz_dates[0] == datetime(2026, 1, 20)
        assert jazz_dates[1] == datetime(2026, 1, 21)
        assert jazz_dates[2] == datetime(2026, 1, 22)

    def test_scrape_extracts_image_urls(self, scraper, sample_html):
        """Test that image URLs are correctly extracted."""
        mock_response = MagicMock()
        mock_response.text = sample_html
        mock_response.raise_for_status = MagicMock()

        with patch.object(scraper.session, "get", return_value=mock_response):
            events = scraper.scrape()

        # Find event with image
        events_with_images = [e for e in events if e.image_url]
        assert len(events_with_images) > 0

        # Check that relative URLs are converted to absolute
        for event in events_with_images:
            assert event.image_url.startswith("http")

    def test_scrape_handles_different_locations(self, scraper, sample_html):
        """Test that different locations are correctly extracted."""
        mock_response = MagicMock()
        mock_response.text = sample_html
        mock_response.raise_for_status = MagicMock()

        with patch.object(scraper.session, "get", return_value=mock_response):
            events = scraper.scrape()

        locations = {e.location for e in events if e.location}
        assert "Frankfurt am Main" in locations
        assert "Hanau" in locations

    def test_scrape_generates_unique_ids_per_date(self, scraper, sample_html):
        """Test that each event occurrence has a unique ID."""
        mock_response = MagicMock()
        mock_response.text = sample_html
        mock_response.raise_for_status = MagicMock()

        with patch.object(scraper.session, "get", return_value=mock_response):
            events = scraper.scrape()

        # All IDs should be unique
        ids = [e.id for e in events]
        assert len(ids) == len(set(ids))

    def test_scrape_handles_network_error(self, scraper):
        """Test that network errors are handled gracefully."""
        with patch.object(scraper, "fetch_page", return_value=None):
            events = scraper.scrape()

        assert events == []

    def test_scrape_handles_malformed_html(self, scraper):
        """Test that malformed HTML is handled gracefully."""
        malformed_html = "<html><body>No events here</body></html>"
        mock_response = MagicMock()
        mock_response.text = malformed_html
        mock_response.raise_for_status = MagicMock()

        with patch.object(scraper.session, "get", return_value=mock_response):
            events = scraper.scrape()

        # Should return empty list, not crash
        assert events == []

    def test_scrape_handles_partial_event_data(self, scraper):
        """Test that events with missing data are handled gracefully."""
        partial_html = """
        <html>
        <body>
            <a href="/Datum/18-Januar-2026/test/">
                <!-- Missing title and dates -->
            </a>
            <a href="/Datum/19-Januar-2026/valid-event/">
                <h3>Valid Event</h3>
                <p>Termine in Frankfurt am Main: 19.1.26</p>
            </a>
        </body>
        </html>
        """
        mock_response = MagicMock()
        mock_response.text = partial_html
        mock_response.raise_for_status = MagicMock()

        with patch.object(scraper.session, "get", return_value=mock_response):
            events = scraper.scrape()

        # Should get at least the valid event
        assert len(events) >= 1
        valid_events = [e for e in events if e.title == "Valid Event"]
        assert len(valid_events) == 1


class TestFrankfurtScraperEventURLs:
    """Tests for URL extraction and handling."""

    @pytest.fixture
    def scraper(self):
        """Create a scraper instance."""
        return FrankfurtScraper()

    def test_relative_urls_converted_to_absolute(self, scraper):
        """Test that relative URLs are converted to absolute URLs."""
        html = """
        <html>
        <body>
            <a href="/Datum/18-Januar-2026/test-event/123/">
                <h3>Test Event</h3>
                <p>Termine in Frankfurt: 18.1.26</p>
            </a>
        </body>
        </html>
        """
        mock_response = MagicMock()
        mock_response.text = html
        mock_response.raise_for_status = MagicMock()

        with patch.object(scraper.session, "get", return_value=mock_response):
            events = scraper.scrape()

        assert len(events) == 1
        assert events[0].url.startswith("https://www.frankfurter-stadtevents.de")

    def test_absolute_urls_preserved(self, scraper):
        """Test that absolute URLs are preserved as-is."""
        html = """
        <html>
        <body>
            <a href="https://www.external-site.com/Datum/18-Januar-2026/test/">
                <h3>External Event</h3>
                <p>Termine in Frankfurt: 18.1.26</p>
            </a>
        </body>
        </html>
        """
        mock_response = MagicMock()
        mock_response.text = html
        mock_response.raise_for_status = MagicMock()

        with patch.object(scraper.session, "get", return_value=mock_response):
            events = scraper.scrape()

        assert len(events) == 1
        assert events[0].url == "https://www.external-site.com/Datum/18-Januar-2026/test/"
