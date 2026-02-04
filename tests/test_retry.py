"""Tests for retry utility."""

from unittest.mock import patch

import pytest

from utils.retry import retry


class TestRetryDecorator:
    """Tests for the retry decorator."""

    def test_successful_call_no_retry(self):
        """Test that successful call doesn't trigger retry."""
        call_count = 0

        @retry(max_attempts=3, delay=0.01)
        def successful_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = successful_func()

        assert result == "success"
        assert call_count == 1

    def test_retry_on_exception(self):
        """Test that function is retried on exception."""
        call_count = 0

        @retry(max_attempts=3, delay=0.01, exceptions=(ValueError,))
        def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Error")
            return "success"

        result = failing_func()

        assert result == "success"
        assert call_count == 3

    def test_max_attempts_exceeded(self):
        """Test that exception is raised after max attempts."""
        call_count = 0

        @retry(max_attempts=3, delay=0.01, exceptions=(ValueError,))
        def always_failing():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")

        with pytest.raises(ValueError) as exc_info:
            always_failing()

        assert "Always fails" in str(exc_info.value)
        assert call_count == 3

    def test_only_catches_specified_exceptions(self):
        """Test that only specified exceptions trigger retry."""
        call_count = 0

        @retry(max_attempts=3, delay=0.01, exceptions=(ValueError,))
        def raises_type_error():
            nonlocal call_count
            call_count += 1
            raise TypeError("Type error")

        with pytest.raises(TypeError):
            raises_type_error()

        # Should only be called once since TypeError is not in exceptions list
        assert call_count == 1

    def test_backoff_multiplier(self):
        """Test that delay increases with backoff multiplier."""
        sleep_times = []

        @retry(max_attempts=4, delay=0.1, backoff=2.0, exceptions=(ValueError,))
        def failing_func():
            raise ValueError("Error")

        with patch("utils.retry.time.sleep") as mock_sleep:
            mock_sleep.side_effect = lambda x: sleep_times.append(x)

            with pytest.raises(ValueError):
                failing_func()

        # Expected delays: 0.1, 0.2, 0.4 (3 retries between 4 attempts)
        assert len(sleep_times) == 3
        assert sleep_times[0] == pytest.approx(0.1)
        assert sleep_times[1] == pytest.approx(0.2)
        assert sleep_times[2] == pytest.approx(0.4)

    def test_preserves_function_metadata(self):
        """Test that decorator preserves function metadata."""

        @retry(max_attempts=3, delay=0.01)
        def documented_func():
            """This is a docstring."""
            return "result"

        assert documented_func.__name__ == "documented_func"
        assert documented_func.__doc__ == "This is a docstring."

    def test_returns_correct_value(self):
        """Test that decorator returns correct value."""

        @retry(max_attempts=3, delay=0.01)
        def returning_func():
            return {"key": "value", "number": 42}

        result = returning_func()

        assert result == {"key": "value", "number": 42}

    def test_multiple_exception_types(self):
        """Test retry with multiple exception types."""
        call_count = 0
        exceptions_to_raise = [ValueError, TypeError, KeyError]

        @retry(max_attempts=5, delay=0.01, exceptions=(ValueError, TypeError, KeyError))
        def multi_exception_func():
            nonlocal call_count
            call_count += 1
            if call_count <= 3:
                raise exceptions_to_raise[call_count - 1]("Error")
            return "success"

        result = multi_exception_func()

        assert result == "success"
        assert call_count == 4

    def test_with_args_and_kwargs(self):
        """Test that decorator works with function arguments."""
        call_count = 0

        @retry(max_attempts=3, delay=0.01, exceptions=(ValueError,))
        def func_with_args(a, b, c=None):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Error")
            return f"{a}-{b}-{c}"

        result = func_with_args("x", "y", c="z")

        assert result == "x-y-z"
        assert call_count == 2

    @patch("utils.retry.logger")
    def test_logs_warning_on_retry(self, mock_logger):
        """Test that warning is logged on retry."""
        call_count = 0

        @retry(max_attempts=3, delay=0.01, exceptions=(ValueError,))
        def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Test error")
            return "success"

        failing_func()

        mock_logger.warning.assert_called_once()
        warning_call = mock_logger.warning.call_args
        assert "1/3" in warning_call[0][0] % warning_call[0][1:]
        assert "Test error" in str(warning_call[0])
