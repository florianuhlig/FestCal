"""Tests for event deduplication."""

from datetime import datetime

import pytest

from src.models.event import Event
from src.utils.deduplicator import Deduplicator


class TestDeduplicator:
    """Tests for Deduplicator."""

    def test_similarity(self):
        """Test string similarity calculation."""
        dedup = Deduplicator()

        assert dedup.similarity("hello", "hello") == 1.0
        assert dedup.similarity("hello", "Hello") == 1.0  # Case insensitive
        assert dedup.similarity("hello", "world") < 0.5
        assert dedup.similarity("", "") == 0.0

    def test_is_duplicate_same_id(self):
        """Test that events with same ID are duplicates."""
        dedup = Deduplicator()

        event1 = Event(
            id="same-id",
            title="Event A",
            start_datetime=datetime(2024, 6, 15, 10, 0),
            source="test",
        )
        event2 = Event(
            id="same-id",
            title="Different Title",
            start_datetime=datetime(2024, 6, 16, 10, 0),
            source="test",
        )

        assert dedup.is_duplicate(event1, event2)

    def test_is_duplicate_similar_title_same_time(self):
        """Test detecting duplicates by similar title and time."""
        dedup = Deduplicator()

        event1 = Event(
            id="id1",
            title="Frankfurt Summer Festival 2024",
            start_datetime=datetime(2024, 6, 15, 10, 0),
            city="Frankfurt",
            source="source1",
        )
        event2 = Event(
            id="id2",
            title="Frankfurt Summer Festival 2024",
            start_datetime=datetime(2024, 6, 15, 10, 30),
            city="Frankfurt",
            source="source2",
        )

        assert dedup.is_duplicate(event1, event2)

    def test_not_duplicate_different_city(self):
        """Test that same-named events in different cities are not duplicates."""
        dedup = Deduplicator()

        event1 = Event(
            id="id1",
            title="Summer Festival",
            start_datetime=datetime(2024, 6, 15, 10, 0),
            city="Frankfurt",
            source="test",
        )
        event2 = Event(
            id="id2",
            title="Summer Festival",
            start_datetime=datetime(2024, 6, 15, 10, 0),
            city="Wiesbaden",
            source="test",
        )

        assert not dedup.is_duplicate(event1, event2)

    def test_deduplicate_list(self):
        """Test deduplicating a list of events."""
        dedup = Deduplicator()

        events = [
            Event(
                id="id1",
                title="Event A",
                start_datetime=datetime(2024, 6, 15, 10, 0),
                city="Frankfurt",
                source="test",
            ),
            Event(
                id="id2",
                title="Event A",
                start_datetime=datetime(2024, 6, 15, 10, 0),
                city="Frankfurt",
                source="test",
            ),
            Event(
                id="id3",
                title="Event B",
                start_datetime=datetime(2024, 6, 16, 10, 0),
                city="Frankfurt",
                source="test",
            ),
        ]

        unique = dedup.deduplicate(events)
        assert len(unique) == 2
