"""Database handler for event storage."""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ..models.event import Base, Event

logger = logging.getLogger(__name__)


class DatabaseHandler:
    """Handler for SQLite database operations."""

    def __init__(self, db_path: str = "data/events.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(f"sqlite:///{self.db_path}", echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def init_db(self) -> None:
        """Initialize database tables."""
        Base.metadata.create_all(self.engine)
        logger.info(f"Database initialized at {self.db_path}")

    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()

    def add_event(self, event: Event) -> None:
        """Add or update an event in the database."""
        # Fields to update (excluding id and timestamps)
        update_fields = [
            "title", "description", "start_datetime", "end_datetime",
            "location", "address", "city", "postal_code",
            "latitude", "longitude", "category", "organizer",
            "url", "image_url", "price", "source"
        ]
        with self.get_session() as session:
            existing = session.query(Event).filter_by(id=event.id).first()
            if existing:
                for field in update_fields:
                    setattr(existing, field, getattr(event, field))
                existing.updated_at = datetime.utcnow()
            else:
                session.add(event)
            session.commit()

    def add_events(self, events: list[Event]) -> int:
        """Add multiple events to the database. Returns count of added events."""
        count = 0
        # Fields to update (excluding id and timestamps)
        update_fields = [
            "title", "description", "start_datetime", "end_datetime",
            "location", "address", "city", "postal_code",
            "latitude", "longitude", "category", "organizer",
            "url", "image_url", "price", "source"
        ]
        with self.get_session() as session:
            for event in events:
                existing = session.query(Event).filter_by(id=event.id).first()
                if existing:
                    for field in update_fields:
                        setattr(existing, field, getattr(event, field))
                    existing.updated_at = datetime.utcnow()
                else:
                    session.add(event)
                    count += 1
            session.commit()
        return count

    def get_event(self, event_id: str) -> Optional[Event]:
        """Get a single event by ID."""
        with self.get_session() as session:
            return session.query(Event).filter_by(id=event_id).first()

    def get_events(
        self,
        city: Optional[str] = None,
        category: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> list[Event]:
        """Get events with optional filtering."""
        with self.get_session() as session:
            query = session.query(Event)
            if city:
                query = query.filter(Event.city == city)
            if category:
                query = query.filter(Event.category == category)
            if start_date:
                query = query.filter(Event.start_datetime >= start_date)
            if end_date:
                query = query.filter(Event.start_datetime <= end_date)
            query = query.order_by(Event.start_datetime)
            if limit:
                query = query.limit(limit)
            return query.all()

    def get_cities(self) -> list[str]:
        """Get list of unique cities."""
        with self.get_session() as session:
            results = session.query(Event.city).distinct().all()
            return [r[0] for r in results if r[0]]

    def get_categories(self) -> list[str]:
        """Get list of unique categories."""
        with self.get_session() as session:
            results = session.query(Event.category).distinct().all()
            return [r[0] for r in results if r[0]]

    def get_stats(self) -> dict:
        """Get database statistics."""
        with self.get_session() as session:
            total = session.query(Event).count()
            cities = len(self.get_cities())
            categories = len(self.get_categories())
            sources = session.query(Event.source).distinct().count()
            return {
                "total_events": total,
                "cities": cities,
                "categories": categories,
                "sources": sources,
            }

    def delete_old_events(self, before_date: datetime) -> int:
        """Delete events before a given date. Returns count of deleted events."""
        with self.get_session() as session:
            count = session.query(Event).filter(Event.end_datetime < before_date).delete()
            session.commit()
            return count


def main():
    """CLI entrypoint for database operations."""
    if len(sys.argv) > 1 and sys.argv[1] == "init":
        handler = DatabaseHandler()
        handler.init_db()
        print("Database initialized successfully.")
    else:
        print("Usage: python -m src.database.db_handler init")


if __name__ == "__main__":
    main()
