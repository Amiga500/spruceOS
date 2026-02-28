"""Tests for utils.throttle.limit_refresh decorator."""

import time

import pytest

from utils.throttle import limit_refresh


class TestLimitRefresh:
    """Verify the caching / throttle behaviour."""

    def test_caches_result_within_window(self):
        call_count = [0]

        @limit_refresh(seconds=10)
        def expensive():
            call_count[0] += 1
            return call_count[0]

        assert expensive() == 1
        assert expensive() == 1  # cached
        assert call_count[0] == 1

    def test_refreshes_after_window(self):
        call_count = [0]

        @limit_refresh(seconds=0)  # 0-second window → always refresh
        def fast():
            call_count[0] += 1
            return call_count[0]

        assert fast() == 1
        time.sleep(0.01)
        assert fast() == 2

    def test_force_refresh(self):
        call_count = [0]

        @limit_refresh(seconds=60)
        def cached():
            call_count[0] += 1
            return call_count[0]

        assert cached() == 1
        cached.force_refresh()
        assert cached() == 2

    def test_passes_arguments(self):
        @limit_refresh(seconds=0)
        def add(a, b):
            return a + b

        assert add(2, 3) == 5

    def test_kwargs_support(self):
        @limit_refresh(seconds=0)
        def greet(name="World"):
            return f"Hello {name}"

        assert greet(name="Test") == "Hello Test"
