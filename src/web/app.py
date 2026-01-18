"""Flask web application and REST API."""

import os
from datetime import datetime
from typing import Optional

from flask import Flask, Response, jsonify, request
from flask_cors import CORS

from ..calendar.generator import CalendarGenerator
from ..database.db_handler import DatabaseHandler

app = Flask(__name__)
CORS(app)

db_handler = DatabaseHandler()
calendar_generator = CalendarGenerator(db_handler=db_handler)


def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse ISO 8601 date string."""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        return None


@app.route("/api/events", methods=["GET"])
def get_events():
    """Get all events with optional filtering."""
    city = request.args.get("city")
    category = request.args.get("category")
    start_date = parse_date(request.args.get("start_date"))
    end_date = parse_date(request.args.get("end_date"))
    limit = request.args.get("limit", type=int)

    events = db_handler.get_events(
        city=city,
        category=category,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )

    return jsonify([event.to_dict() for event in events])


@app.route("/api/events/<event_id>", methods=["GET"])
def get_event(event_id: str):
    """Get a single event by ID."""
    event = db_handler.get_event(event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404
    return jsonify(event.to_dict())


@app.route("/api/export/ics", methods=["GET"])
def export_ics():
    """Export events as iCalendar file."""
    city = request.args.get("city")
    category = request.args.get("category")
    start_date = parse_date(request.args.get("start_date"))
    end_date = parse_date(request.args.get("end_date"))

    ical_data = calendar_generator.to_ical_bytes(
        city=city,
        category=category,
        start_date=start_date,
        end_date=end_date,
    )

    return Response(
        ical_data,
        mimetype="text/calendar",
        headers={"Content-Disposition": "attachment; filename=events.ics"},
    )


@app.route("/api/cities", methods=["GET"])
def get_cities():
    """Get list of available cities."""
    cities = db_handler.get_cities()
    return jsonify(cities)


@app.route("/api/categories", methods=["GET"])
def get_categories():
    """Get list of available categories."""
    categories = db_handler.get_categories()
    return jsonify(categories)


@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Get database statistics."""
    stats = db_handler.get_stats()
    return jsonify(stats)


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})


def main():
    """Run the Flask development server."""
    host = os.getenv("WEB_HOST", "0.0.0.0")
    port = int(os.getenv("WEB_PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    print(f"Starting web server at http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()
