"""iCalendar generation from events."""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from icalendar import Calendar, Event as ICalEvent

from ..database.db_handler import DatabaseHandler
from ..models.event import Event


class CalendarGenerator:
    """Generate iCalendar files from events."""

    def __init__(
        self,
        calendar_name: str = "Rhein-Main Events",
        db_handler: Optional[DatabaseHandler] = None,
    ):
        self.calendar_name = calendar_name
        self.db_handler = db_handler or DatabaseHandler()

    def create_calendar(
        self,
        events: list[Event],
        name: Optional[str] = None,
    ) -> Calendar:
        """Create an iCalendar from a list of events."""
        cal = Calendar()
        cal.add("prodid", "-//FestCal//Rhein-Main Events//DE")
        cal.add("version", "2.0")
        cal.add("x-wr-calname", name or self.calendar_name)
        cal.add("x-wr-timezone", "Europe/Berlin")

        for event in events:
            ical_event = self._event_to_ical(event)
            cal.add_component(ical_event)

        return cal

    def _event_to_ical(self, event: Event) -> ICalEvent:
        """Convert an Event to an iCalendar event."""
        ical_event = ICalEvent()
        ical_event.add("uid", f"{event.id}@festcal.local")
        ical_event.add("summary", event.title)
        ical_event.add("dtstart", event.start_datetime)

        if event.end_datetime:
            ical_event.add("dtend", event.end_datetime)

        if event.description:
            ical_event.add("description", event.description)

        if event.location:
            location_parts = [event.location]
            if event.address:
                location_parts.append(event.address)
            if event.city:
                location_parts.append(event.city)
            ical_event.add("location", ", ".join(location_parts))

        if event.url:
            ical_event.add("url", event.url)

        if event.category:
            ical_event.add("categories", [event.category])

        if event.organizer:
            ical_event.add("organizer", event.organizer)

        if event.latitude and event.longitude:
            ical_event.add("geo", (event.latitude, event.longitude))

        ical_event.add("dtstamp", datetime.utcnow())

        if event.created_at:
            ical_event.add("created", event.created_at)

        if event.updated_at:
            ical_event.add("last-modified", event.updated_at)

        return ical_event

    def export_to_file(
        self,
        output_path: str,
        city: Optional[str] = None,
        category: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> int:
        """Export events to an .ics file. Returns number of events exported."""
        events = self.db_handler.get_events(
            city=city,
            category=category,
            start_date=start_date,
            end_date=end_date,
        )

        cal = self.create_calendar(events)

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(cal.to_ical())

        return len(events)

    def to_ical_bytes(
        self,
        city: Optional[str] = None,
        category: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> bytes:
        """Generate iCalendar data as bytes."""
        events = self.db_handler.get_events(
            city=city,
            category=category,
            start_date=start_date,
            end_date=end_date,
        )
        cal = self.create_calendar(events)
        return cal.to_ical()


def main():
    """CLI entrypoint for calendar export."""
    parser = argparse.ArgumentParser(description="Export events to iCalendar format")
    parser.add_argument("command", choices=["export"], help="Command to run")
    parser.add_argument("--output", "-o", required=True, help="Output file path")
    parser.add_argument("--city", help="Filter by city")
    parser.add_argument("--category", help="Filter by category")

    args = parser.parse_args()

    if args.command == "export":
        generator = CalendarGenerator()
        count = generator.export_to_file(
            args.output,
            city=args.city,
            category=args.category,
        )
        print(f"Exported {count} events to {args.output}")


if __name__ == "__main__":
    main()
