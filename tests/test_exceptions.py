"""Tests for custom exceptions."""

from exceptions import (
    ApiConnectionError,
    ApiResponseError,
    ExportError,
    InvalidRequestError,
    ProcessNotFoundError,
    ScraperException,
)


class TestScraperException:
    """Tests for the base ScraperException."""

    def test_is_base_exception(self):
        """Test that ScraperException inherits from Exception."""
        exc = ScraperException("Test error")
        assert isinstance(exc, Exception)

    def test_message(self):
        """Test that exception message is set correctly."""
        exc = ScraperException("Test error message")
        assert str(exc) == "Test error message"


class TestInvalidRequestError:
    """Tests for InvalidRequestError."""

    def test_inherits_from_scraper_exception(self):
        """Test that InvalidRequestError inherits from ScraperException."""
        exc = InvalidRequestError("Invalid request")
        assert isinstance(exc, ScraperException)

    def test_message(self):
        """Test that exception message is set correctly."""
        exc = InvalidRequestError("Invalid request format")
        assert str(exc) == "Invalid request format"


class TestProcessNotFoundError:
    """Tests for ProcessNotFoundError."""

    def test_inherits_from_scraper_exception(self):
        """Test that ProcessNotFoundError inherits from ScraperException."""
        exc = ProcessNotFoundError("No process found")
        assert isinstance(exc, ScraperException)


class TestApiConnectionError:
    """Tests for ApiConnectionError."""

    def test_inherits_from_scraper_exception(self):
        """Test that ApiConnectionError inherits from ScraperException."""
        exc = ApiConnectionError("Connection failed")
        assert isinstance(exc, ScraperException)

    def test_with_url_and_status_code(self):
        """Test that ApiConnectionError stores URL and status code."""
        exc = ApiConnectionError(
            "HTTP Error 404", url="https://api.example.com", status_code=404
        )
        assert exc.url == "https://api.example.com"
        assert exc.status_code == 404
        assert str(exc) == "HTTP Error 404"

    def test_without_optional_params(self):
        """Test that optional params default to None."""
        exc = ApiConnectionError("Connection failed")
        assert exc.url is None
        assert exc.status_code is None


class TestApiResponseError:
    """Tests for ApiResponseError."""

    def test_inherits_from_scraper_exception(self):
        """Test that ApiResponseError inherits from ScraperException."""
        exc = ApiResponseError("Invalid JSON")
        assert isinstance(exc, ScraperException)


class TestExportError:
    """Tests for ExportError."""

    def test_inherits_from_scraper_exception(self):
        """Test that ExportError inherits from ScraperException."""
        exc = ExportError("Export failed")
        assert isinstance(exc, ScraperException)
