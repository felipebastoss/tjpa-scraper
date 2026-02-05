"""Logging configuration for the scraper."""

import logging
import os
import sys
from datetime import datetime


def setup_logging(
    base_dir: str, log_dir: str = "logs", level: int = logging.INFO
) -> logging.Logger:
    """
    Configure logging for the application.

    Args:
        log_dir: Directory to store log files
        level: Logging level

    Returns:
        Configured logger instance
    """
    os.makedirs(os.path.join(base_dir, log_dir), exist_ok=True)

    logger = logging.getLogger("tjpa_scraper")
    logger.setLevel(level)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter("%(levelname)s - %(message)s")
    console_handler.setFormatter(console_format)

    # File handler
    log_file = os.path.join(
        log_dir, f"scraper_{datetime.now():%Y%m%d_%H%M%S}.log"
    )
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - "
        "%(funcName)s:%(lineno)d - %(message)s"
    )
    file_handler.setFormatter(file_format)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
