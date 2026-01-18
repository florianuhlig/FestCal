"""Tests for calendar generation."""

from datetime import datetime

import pytest

from src.calendar.generator import CalendarGenerator
from src.models.event import Event


class TestCalendarGenerator:
    """Tests for CalendarGenerator."""

    def test_create_empty_calendar(self):
        """Test creating calendar with no events."""
        generator = CalendarGenerator(calendar_name="Test Calendar")
        cal = generator.create_calendar([])

        assert cal is not None
        assert cal["x-wr-calname"] == "Test Calendar"

    def test_event_to_ical(self):
        """Test converting Event to iCalendar event."""
        generator = CalendarGenerator()

        event = Event(
            id="test123",
            title="Test Event",
            description="A test event",
            start_datetime=datetime(2024, 6, 15, 14, 0),
            end_datetime=datetime(2024, 6, 15, 18, 0),
            location="Test Location",
            city="Frankfurt",
            source="test",
        )

        ical_event = generator._event_to_ical(event)

        assert ical_event["summary"] == "Test Event"
        assert "test123" in str(ical_event["uid"])

    def test_create_calendar_with_events(self):
        """Test creating calendar with events."""
        generator = CalendarGenerator()

        events = [
            Event(
                id="event1",
                title="Event 1",
                start_datetime=datetime(2024, 6, 15, 10, 0),
                source="test",
            ),
            Event(
                id="event2",
                title="Event 2",
                start_datetime=datetime(2024, 6, 16, 14, 0),
                source="test",
            ),
        ]

        cal = generator.create_calendar(events)
        components = list(cal.walk("VEVENT"))

        assert len(components) == 2
