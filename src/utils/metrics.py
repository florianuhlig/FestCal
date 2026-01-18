"""Metrics collection for scraping operations."""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class ScrapeMetrics:
    """Metrics for a single scraping operation."""

    source_name: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    events_found: int = 0
    events_valid: int = 0
    events_stored: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def start(self) -> None:
        """Mark the start of the scraping operation."""
        self.start_time = datetime.utcnow()

    def finish(self) -> None:
        """Mark the end of the scraping operation."""
        self.end_time = datetime.utcnow()

    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    @property
    def success_rate(self) -> float:
        """Calculate the success rate (valid events / found events)."""
        if self.events_found == 0:
            return 0.0
        return self.events_valid / self.events_found

    @property
    def has_errors(self) -> bool:
        """Check if any errors occurred."""
        return len(self.errors) > 0

    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)
        logger.error(f"[{self.source_name}] {error}")

    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)
        logger.warning(f"[{self.source_name}] {warning}")

    def to_dict(self) -> dict:
        """Convert metrics to dictionary."""
        return {
            "source_name": self.source_name,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "events_found": self.events_found,
            "events_valid": self.events_valid,
            "events_stored": self.events_stored,
            "success_rate": self.success_rate,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings,
        }

    def log_summary(self) -> None:
        """Log a summary of the scraping operation."""
        duration = self.duration_seconds or 0
        logger.info(
            f"[{self.source_name}] Scrape complete: "
            f"{self.events_found} found, {self.events_valid} valid, "
            f"{self.events_stored} stored in {duration:.2f}s "
            f"({len(self.errors)} errors, {len(self.warnings)} warnings)"
        )


@dataclass
class AggregateMetrics:
    """Aggregated metrics across multiple scraping operations."""

    scrapes: list[ScrapeMetrics] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    def start(self) -> None:
        """Mark the start of the aggregate operation."""
        self.start_time = datetime.utcnow()

    def finish(self) -> None:
        """Mark the end of the aggregate operation."""
        self.end_time = datetime.utcnow()

    def add_scrape(self, metrics: ScrapeMetrics) -> None:
        """Add a scrape result to the aggregate."""
        self.scrapes.append(metrics)

    @property
    def total_events_found(self) -> int:
        """Total events found across all scrapes."""
        return sum(s.events_found for s in self.scrapes)

    @property
    def total_events_valid(self) -> int:
        """Total valid events across all scrapes."""
        return sum(s.events_valid for s in self.scrapes)

    @property
    def total_events_stored(self) -> int:
        """Total events stored across all scrapes."""
        return sum(s.events_stored for s in self.scrapes)

    @property
    def total_errors(self) -> int:
        """Total errors across all scrapes."""
        return sum(len(s.errors) for s in self.scrapes)

    @property
    def total_warnings(self) -> int:
        """Total warnings across all scrapes."""
        return sum(len(s.warnings) for s in self.scrapes)

    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate total duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    @property
    def sources_succeeded(self) -> int:
        """Count of sources that succeeded without errors."""
        return sum(1 for s in self.scrapes if not s.has_errors)

    @property
    def sources_failed(self) -> int:
        """Count of sources that had errors."""
        return sum(1 for s in self.scrapes if s.has_errors)

    def to_dict(self) -> dict:
        """Convert aggregate metrics to dictionary."""
        return {
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "sources_total": len(self.scrapes),
            "sources_succeeded": self.sources_succeeded,
            "sources_failed": self.sources_failed,
            "total_events_found": self.total_events_found,
            "total_events_valid": self.total_events_valid,
            "total_events_stored": self.total_events_stored,
            "total_errors": self.total_errors,
            "total_warnings": self.total_warnings,
            "scrapes": [s.to_dict() for s in self.scrapes],
        }

    def log_summary(self) -> None:
        """Log a summary of the aggregate operation."""
        duration = self.duration_seconds or 0
        logger.info(
            f"Scraping complete: {len(self.scrapes)} sources, "
            f"{self.sources_succeeded} succeeded, {self.sources_failed} failed. "
            f"Total: {self.total_events_found} found, {self.total_events_stored} stored "
            f"in {duration:.2f}s"
        )


class MetricsTimer:
    """Context manager for timing operations."""

    def __init__(self):
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.end_time = time.perf_counter()

    @property
    def elapsed(self) -> float:
        """Get elapsed time in seconds."""
        if self.start_time is None:
            return 0.0
        end = self.end_time if self.end_time else time.perf_counter()
        return end - self.start_time
