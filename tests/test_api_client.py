"""Tests for API client."""

import json
from unittest.mock import MagicMock, patch

import pytest

from client.api_client import ApiClient
from config import ScraperConfig
from exceptions import ApiConnectionError, ApiResponseError
from urllib.error import URLError, HTTPError


class TestApiClient:
    """Tests for the ApiClient class."""

    @pytest.fixture
    def api_client(self, scraper_config):
        """Return an ApiClient instance with minimal wait time."""
        scraper_config.min_wait_time = 0.0
        scraper_config.max_wait_time = 0.01
        return ApiClient(config=scraper_config)

    @patch("client.api_client.urlopen")
    @patch("client.api_client.time.sleep")
    def test_get_success(self, mock_sleep, mock_urlopen, api_client):
        """Test successful GET request."""
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = b'{"status": "ok"}'
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = api_client.get("/test/endpoint")

        assert result == {"status": "ok"}
        mock_urlopen.assert_called_once()

    @patch("client.api_client.urlopen")
    @patch("client.api_client.time.sleep")
    def test_get_returns_empty_list_on_204(self, mock_sleep, mock_urlopen, api_client):
        """Test GET request returns empty list on 204 No Content."""
        mock_response = MagicMock()
        mock_response.getcode.return_value = 204
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = api_client.get("/test/endpoint")

        assert result == []

    @patch("client.api_client.urlopen")
    @patch("client.api_client.time.sleep")
    def test_get_constructs_full_url(self, mock_sleep, mock_urlopen, api_client):
        """Test GET request constructs full URL correctly."""
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = b"{}"
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        api_client.get("/test/endpoint")

        # Check that urlopen was called with the correct URL
        call_args = mock_urlopen.call_args
        request_obj = call_args[0][0]
        expected_url = (
            f"{api_client.config.base_url}"
            f"{api_client.config.base_api_route}"
            "/test/endpoint"
        )
        assert request_obj.full_url == expected_url

    @patch("client.api_client.urlopen")
    @patch("client.api_client.time.sleep")
    def test_get_http_error(self, mock_sleep, mock_urlopen, api_client):
        """Test GET request handles HTTP errors."""
        mock_urlopen.side_effect = HTTPError(
            url="https://test.com",
            code=404,
            msg="Not Found",
            hdrs={},
            fp=None,
        )

        with pytest.raises(ApiConnectionError) as exc_info:
            api_client.get("/test/endpoint")

        assert exc_info.value.status_code == 404
        assert "404" in str(exc_info.value)

    @patch("client.api_client.urlopen")
    @patch("client.api_client.time.sleep")
    def test_get_url_error(self, mock_sleep, mock_urlopen, api_client):
        """Test GET request handles URL errors."""
        mock_urlopen.side_effect = URLError("Connection refused")

        with pytest.raises(ApiConnectionError) as exc_info:
            api_client.get("/test/endpoint")

        assert "Connection failed" in str(exc_info.value)

    @patch("client.api_client.urlopen")
    @patch("client.api_client.time.sleep")
    def test_get_invalid_json(self, mock_sleep, mock_urlopen, api_client):
        """Test GET request handles invalid JSON response."""
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = b"not valid json"
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        with pytest.raises(ApiResponseError) as exc_info:
            api_client.get("/test/endpoint")

        assert "Invalid JSON" in str(exc_info.value)

    @patch("client.api_client.urlopen")
    @patch("client.api_client.time.sleep")
    def test_get_timeout(self, mock_sleep, mock_urlopen, api_client):
        """Test GET request handles timeout."""
        mock_urlopen.side_effect = TimeoutError()

        with pytest.raises(ApiConnectionError) as exc_info:
            api_client.get("/test/endpoint")

        assert "timed out" in str(exc_info.value)

    @patch("client.api_client.random.uniform")
    @patch("client.api_client.time.sleep")
    @patch("client.api_client.urlopen")
    def test_wait_is_called(self, mock_urlopen, mock_sleep, mock_uniform, api_client):
        """Test that rate limiting wait is applied."""
        mock_uniform.return_value = 1.5
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = b"{}"
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        api_client.get("/test/endpoint")

        mock_sleep.assert_called_once_with(1.5)

    @patch("client.api_client.urlopen")
    @patch("client.api_client.time.sleep")
    def test_user_agent_is_set(self, mock_sleep, mock_urlopen, api_client):
        """Test that User-Agent header is set."""
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = b"{}"
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        api_client.get("/test/endpoint")

        call_args = mock_urlopen.call_args
        request_obj = call_args[0][0]
        assert request_obj.get_header("User-agent") == api_client.config.user_agent
