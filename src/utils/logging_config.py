"""Centralized logging configuration for FestCal."""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    log_format: Optional[str] = None,
) -> logging.Logger:
    """Configure logging for the application.

    Args:
        level: Logging level (e.g., logging.INFO, logging.DEBUG)
        log_file: Optional path to log file. If provided, logs to both file and console.
        log_format: Optional custom format string. Uses default if not provided.

    Returns:
        The root logger configured for the application.
    """
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(log_format)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module.

    Args:
        name: The name of the module (typically __name__)

    Returns:
        A logger instance for the module.
    """
    return logging.getLogger(name)


# Convenience function for quick setup
def setup_default_logging(debug: bool = False) -> logging.Logger:
    """Setup logging with sensible defaults.

    Args:
        debug: If True, sets level to DEBUG. Otherwise INFO.

    Returns:
        The configured root logger.
    """
    level = logging.DEBUG if debug else logging.INFO
    return setup_logging(level=level)
