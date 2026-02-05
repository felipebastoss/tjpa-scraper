"""API client to handle requests to the TJPA API."""

import json
import random
import time
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from config import ScraperConfig
from exceptions import ApiConnectionError, ApiResponseError
from utils.retry import retry


@dataclass
class ApiClient:
    """
    Client to handle API requests.
    """

    config: ScraperConfig

    @retry(
        max_attempts=3,
        delay=1.0,
        backoff=2.0,
        exceptions=(ApiConnectionError, ApiResponseError, TimeoutError),
    )
    def get(self, url: str) -> Any:
        """
        Perform a GET request to the specified URL and return the JSON response
        """
        full_url = f"{self.config.base_url}{self.config.base_api_route}{url}"
        self._wait()
        try:
            request = Request(
                full_url,
                headers={
                    "User-Agent": self.config.user_agent,
                },
            )
            with urlopen(
                request, timeout=self.config.request_timeout
            ) as request_response:
                if request_response.getcode() == 204:
                    return []
                return json.loads(request_response.read().decode("utf-8"))
        except HTTPError as e:
            raise ApiConnectionError(
                f"HTTP Error {e.code}: {e.reason}",
                url=full_url,
                status_code=e.code,
            ) from e
        except URLError as e:
            raise ApiConnectionError(
                f"Connection failed: {e.reason}",
                url=full_url,
            ) from e
        except json.JSONDecodeError as e:
            raise ApiResponseError(f"Invalid JSON response: {e}") from e
        except TimeoutError:
            raise ApiConnectionError(
                f"Request timed out after {self.config.request_timeout}s",
                url=full_url,
            ) from None

    def _wait(self) -> None:
        """Apply rate limiting with random delay."""
        wait_time = random.uniform(
            self.config.min_wait_time,
            self.config.max_wait_time,
        )
        time.sleep(wait_time)
