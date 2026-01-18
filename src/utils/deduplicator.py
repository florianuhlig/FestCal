"""Event deduplication utilities."""

from datetime import datetime, timedelta
from difflib import SequenceMatcher
from typing import Optional

from ..models.event import Event


class Deduplicator:
    """Detect and remove duplicate events."""

    def __init__(
        self,
        title_threshold: float = 0.85,
        time_window_minutes: int = 60,
    ):
        self.title_threshold = title_threshold
        self.time_window = timedelta(minutes=time_window_minutes)

    def similarity(self, a: str, b: str) -> float:
        """Calculate similarity ratio between two strings."""
        if not a or not b:
            return 0.0
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def is_duplicate(self, event1: Event, event2: Event) -> bool:
        """Check if two events are duplicates."""
        if event1.id == event2.id:
            return True

        # Check title similarity
        title_sim = self.similarity(event1.title, event2.title)
        if title_sim < self.title_threshold:
            return False

        # Check time proximity
        if event1.start_datetime and event2.start_datetime:
            time_diff = abs(event1.start_datetime - event2.start_datetime)
            if time_diff > self.time_window:
                return False

        # Check location if available
        if event1.city and event2.city:
            if event1.city.lower() != event2.city.lower():
                return False

        return True

    def deduplicate(self, events: list[Event]) -> list[Event]:
        """Remove duplicate events from a list. Keeps the first occurrence."""
        unique_events = []

        for event in events:
            is_dup = False
            for unique in unique_events:
                if self.is_duplicate(event, unique):
                    is_dup = True
                    break
            if not is_dup:
                unique_events.append(event)

        return unique_events

    def find_duplicates(self, events: list[Event]) -> list[tuple[Event, Event]]:
        """Find all duplicate pairs in a list of events."""
        duplicates = []

        for i, event1 in enumerate(events):
            for event2 in events[i + 1:]:
                if self.is_duplicate(event1, event2):
                    duplicates.append((event1, event2))

        return duplicates
