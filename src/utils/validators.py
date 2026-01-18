"""Event validation utilities."""

from urllib.parse import urlparse

from ..models.event import Event


class ValidationError(Exception):
    """Raised when event validation fails."""

    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


def validate_event(event: Event, strict: bool = False) -> list[ValidationError]:
    """
    Validate an event and return list of validation errors.

    Args:
        event: Event to validate
        strict: If True, also validate optional fields

    Returns:
        List of ValidationError objects (empty if valid)
    """
    errors = []

    # Required fields
    if not event.id:
        errors.append(ValidationError("id", "Event ID is required"))

    if not event.title or not event.title.strip():
        errors.append(ValidationError("title", "Event title is required"))

    if not event.start_datetime:
        errors.append(ValidationError("start_datetime", "Start datetime is required"))

    if not event.source:
        errors.append(ValidationError("source", "Event source is required"))

    # Date validation
    if event.start_datetime and event.end_datetime:
        if event.end_datetime < event.start_datetime:
            errors.append(
                ValidationError("end_datetime", "End datetime must be after start datetime")
            )

    # URL validation
    if event.url and strict:
        try:
            result = urlparse(event.url)
            if not all([result.scheme, result.netloc]):
                errors.append(ValidationError("url", "Invalid URL format"))
        except Exception:
            errors.append(ValidationError("url", "Invalid URL format"))

    if event.image_url and strict:
        try:
            result = urlparse(event.image_url)
            if not all([result.scheme, result.netloc]):
                errors.append(ValidationError("image_url", "Invalid image URL format"))
        except Exception:
            errors.append(ValidationError("image_url", "Invalid image URL format"))

    # Postal code validation (German format)
    if event.postal_code and strict:
        if not event.postal_code.isdigit() or len(event.postal_code) != 5:
            errors.append(
                ValidationError(
                    "postal_code", "Invalid German postal code format (expected 5 digits)"
                )
            )

    return errors


def is_valid_event(event: Event, strict: bool = False) -> bool:
    """Check if an event is valid."""
    return len(validate_event(event, strict)) == 0
