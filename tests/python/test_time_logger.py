"""Tests for utils.time_logger.log_timing context manager."""

import logging
import time

import pytest

from utils.time_logger import log_timing


class TestLogTiming:

    def test_logs_completion_message(self, caplog):
        logger = logging.getLogger("test_timing")
        with caplog.at_level(logging.INFO, logger="test_timing"):
            with log_timing("Test operation", logger):
                time.sleep(0.01)

        assert any("Test operation completed in" in msg for msg in caplog.messages)

    def test_timing_value_is_reasonable(self, caplog):
        logger = logging.getLogger("test_timing2")
        with caplog.at_level(logging.INFO, logger="test_timing2"):
            with log_timing("Quick op", logger):
                pass

        # Should complete in well under 1 second
        for msg in caplog.messages:
            if "Quick op completed in" in msg:
                # Extract the float seconds value
                seconds_str = msg.split("in ")[1].rstrip("s")
                assert float(seconds_str) < 1.0

    def test_propagates_exception(self):
        logger = logging.getLogger("test_timing3")
        with pytest.raises(ValueError, match="test error"):
            with log_timing("Failing op", logger):
                raise ValueError("test error")

    def test_logs_even_on_exception(self, caplog):
        logger = logging.getLogger("test_timing4")
        with caplog.at_level(logging.INFO, logger="test_timing4"):
            try:
                with log_timing("Error op", logger):
                    raise RuntimeError("boom")
            except RuntimeError:
                pass

        assert any("Error op completed in" in msg for msg in caplog.messages)
