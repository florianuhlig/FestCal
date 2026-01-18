"""Event data model."""

from sqlalchemy import Column, DateTime, Float, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Event(Base):
    """Represents an event in the Rhein-Main region."""

    __tablename__ = "events"

    id = Column(String(255), primary_key=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime)
    location = Column(String(500))
    address = Column(String(500))
    city = Column(String(100))
    postal_code = Column(String(20))
    category = Column(String(100))
    organizer = Column(String(255))
    url = Column(String(1000))
    image_url = Column(String(1000))
    price = Column(String(255))
    source = Column(String(255), nullable=False)

    def __repr__(self) -> str:
        return f"<Event(id={self.id}, title={self.title}, city={self.city})>"

    def to_dict(self) -> dict:
        """Convert event to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "start_datetime": self.start_datetime.isoformat() if self.start_datetime else None,
            "end_datetime": self.end_datetime.isoformat() if self.end_datetime else None,
            "location": self.location,
            "address": self.address,
            "city": self.city,
            "postal_code": self.postal_code,
            "category": self.category,
            "organizer": self.organizer,
            "url": self.url,
            "image_url": self.image_url,
            "price": self.price,
            "source": self.source,
        }
