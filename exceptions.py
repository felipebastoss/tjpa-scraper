"""Custom exceptions for the TJPA scraper."""


class ScraperException(Exception):
    """Base exception for all scraper errors."""


class InvalidRequestError(ScraperException):
    """Raised when the request format is invalid."""


class ProcessNotFoundError(ScraperException):
    """Raised when no processes are found."""


class ApiConnectionError(ScraperException):
    """Raised when API connection fails."""

    def __init__(self, message: str, url: str = None, status_code: int = None):
        super().__init__(message)
        self.url = url
        self.status_code = status_code


class ApiResponseError(ScraperException):
    """Raised when API returns an unexpected response."""


class ExportError(ScraperException):
    """Raised when export operation fails."""
