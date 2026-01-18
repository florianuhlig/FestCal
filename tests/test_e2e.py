"""End-to-end tests for the FestCal pipeline."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.calendar.generator import CalendarGenerator
from src.database.db_handler import DatabaseHandler
from src.scrapers.frankfurt_scraper import FrankfurtScraper


class TestFullPipeline:
    """End-to-end tests: Scrape -> Store -> Export."""

    @pytest.fixture
    def sample_html(self):
        """Load sample HTML fixture."""
        fixture_path = Path(__file__).parent / "fixtures" / "frankfurt_events_page.html"
        return fixture_path.read_text(encoding="utf-8")

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        handler = DatabaseHandler(db_path=db_path)
        handler.init_db()
        yield handler

        # Cleanup
        Path(db_path).unlink(missing_ok=True)

    @pytest.fixture
    def temp_ics_path(self):
        """Create a temporary path for ICS export."""
        with tempfile.NamedTemporaryFile(suffix=".ics", delete=False) as f:
            ics_path = f.name

        yield ics_path

        # Cleanup
        Path(ics_path).unlink(missing_ok=True)

    def test_scrape_store_export_pipeline(self, sample_html, temp_db, temp_ics_path):
        """Test the complete pipeline: scrape events, store in DB, export to ICS."""
        # Step 1: Scrape events (mocked)
        scraper = FrankfurtScraper()
        mock_response = MagicMock()
        mock_response.text = sample_html
        mock_response.raise_for_status = MagicMock()

        with patch.object(scraper.session, "get", return_value=mock_response):
            events = scraper.scrape()

        assert len(events) > 0, "Scraping should return events"

        # Step 2: Store events in database
        added = temp_db.add_events(events)
        assert added == len(events), "All events should be added to database"

        # Verify events are in database
        stored_events = temp_db.get_events()
        assert len(stored_events) == len(events)

        # Step 3: Export to ICS
        generator = CalendarGenerator(db_handler=temp_db)
        exported_count = generator.export_to_file(temp_ics_path)

        assert exported_count == len(events), "All events should be exported"
        assert Path(temp_ics_path).exists(), "ICS file should be created"

        # Verify ICS content
        ics_content = Path(temp_ics_path).read_text(encoding="utf-8")
        assert "BEGIN:VCALENDAR" in ics_content
        assert "BEGIN:VEVENT" in ics_content
        assert "END:VCALENDAR" in ics_content

    def test_events_flow_preserves_data(self, sample_html, temp_db, temp_ics_path):
        """Test that event data is preserved through the pipeline."""
        # Scrape events
        scraper = FrankfurtScraper()
        mock_response = MagicMock()
        mock_response.text = sample_html
        mock_response.raise_for_status = MagicMock()

        with patch.object(scraper.session, "get", return_value=mock_response):
            scraped_events = scraper.scrape()

        # Collect titles before storing (Event objects are in transient state)
        scraped_titles = {e.title for e in scraped_events}
        scraped_count = len(scraped_events)

        # Store and retrieve
        temp_db.add_events(scraped_events)
        stored_events = temp_db.get_events()

        # Verify data integrity
        stored_titles = {e.title for e in stored_events}
        assert scraped_titles == stored_titles
        assert len(stored_events) == scraped_count

        # Check specific event details
        jazz_events = [e for e in stored_events if "Jazz" in e.title]
        assert len(jazz_events) == 3  # Multi-date event

    def test_duplicate_events_handled(self, sample_html, temp_db):
        """Test that running the scraper twice doesn't create duplicates."""
        scraper = FrankfurtScraper()
        mock_response = MagicMock()
        mock_response.text = sample_html
        mock_response.raise_for_status = MagicMock()

        # First scrape
        with patch.object(scraper.session, "get", return_value=mock_response):
            events1 = scraper.scrape()
        events1_count = len(events1)
        added1 = temp_db.add_events(events1)

        # Second scrape (same data) - need new scraper instance for clean session
        scraper2 = FrankfurtScraper()
        with patch.object(scraper2.session, "get", return_value=mock_response):
            events2 = scraper2.scrape()
        added2 = temp_db.add_events(events2)

        # First run should add events, second should add zero (updates instead)
        assert added1 > 0
        assert added1 == events1_count
        assert added2 == 0

        # Total in database should equal first run
        total = len(temp_db.get_events())
        assert total == added1

    def test_ics_file_valid_format(self, sample_html, temp_db, temp_ics_path):
        """Test that the exported ICS file has valid format."""
        # Setup data
        scraper = FrankfurtScraper()
        mock_response = MagicMock()
        mock_response.text = sample_html
        mock_response.raise_for_status = MagicMock()

        with patch.object(scraper.session, "get", return_value=mock_response):
            events = scraper.scrape()

        temp_db.add_events(events)

        # Export
        generator = CalendarGenerator(db_handler=temp_db)
        generator.export_to_file(temp_ics_path)

        # Verify ICS structure
        ics_content = Path(temp_ics_path).read_text(encoding="utf-8")

        # Check required iCalendar properties
        assert "PRODID:" in ics_content
        assert "VERSION:2.0" in ics_content
        assert "X-WR-CALNAME:" in ics_content

        # Check event structure
        vevent_count = ics_content.count("BEGIN:VEVENT")
        end_vevent_count = ics_content.count("END:VEVENT")
        assert vevent_count == end_vevent_count
        assert vevent_count == len(events)

    def test_database_filtering_works(self, sample_html, temp_db):
        """Test that database filtering returns correct events."""
        # Setup data
        scraper = FrankfurtScraper()
        mock_response = MagicMock()
        mock_response.text = sample_html
        mock_response.raise_for_status = MagicMock()

        with patch.object(scraper.session, "get", return_value=mock_response):
            events = scraper.scrape()

        temp_db.add_events(events)

        # Test filtering by city (all events should be in Frankfurt am Main per scraper)
        frankfurt_events = temp_db.get_events(city="Frankfurt am Main")
        assert len(frankfurt_events) > 0

    def test_empty_database_export(self, temp_db, temp_ics_path):
        """Test exporting from an empty database."""
        generator = CalendarGenerator(db_handler=temp_db)
        exported_count = generator.export_to_file(temp_ics_path)

        assert exported_count == 0
        assert Path(temp_ics_path).exists()

        # Should still be valid iCal format
        ics_content = Path(temp_ics_path).read_text(encoding="utf-8")
        assert "BEGIN:VCALENDAR" in ics_content
        assert "END:VCALENDAR" in ics_content


class TestDatabaseStats:
    """Tests for database statistics."""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        handler = DatabaseHandler(db_path=db_path)
        handler.init_db()
        yield handler

        Path(db_path).unlink(missing_ok=True)

    @pytest.fixture
    def sample_html(self):
        """Load sample HTML fixture."""
        fixture_path = Path(__file__).parent / "fixtures" / "frankfurt_events_page.html"
        return fixture_path.read_text(encoding="utf-8")

    def test_stats_after_import(self, sample_html, temp_db):
        """Test database stats after importing events."""
        # Setup data
        scraper = FrankfurtScraper()
        mock_response = MagicMock()
        mock_response.text = sample_html
        mock_response.raise_for_status = MagicMock()

        with patch.object(scraper.session, "get", return_value=mock_response):
            events = scraper.scrape()

        temp_db.add_events(events)

        # Get stats
        stats = temp_db.get_stats()

        assert stats["total_events"] == len(events)
        assert stats["sources"] >= 1
        assert stats["cities"] >= 1
