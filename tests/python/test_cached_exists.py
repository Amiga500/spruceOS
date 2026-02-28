"""Tests for utils.cached_exists.CachedExists."""

import os

import pytest

from utils.cached_exists import CachedExists


@pytest.fixture(autouse=True)
def clear_cache():
    CachedExists.clear()
    yield
    CachedExists.clear()


class TestExists:
    """Core exists() behaviour."""

    def test_returns_true_for_existing_file(self, tmp_path):
        f = tmp_path / "hello.txt"
        f.write_text("hi")
        assert CachedExists.exists(str(f)) is True

    def test_returns_false_for_missing_file(self, tmp_path):
        assert CachedExists.exists(str(tmp_path / "nope.txt")) is False

    def test_result_is_cached(self, tmp_path):
        f = tmp_path / "cached.txt"
        f.write_text("data")
        # First call populates cache
        assert CachedExists.exists(str(f)) is True
        # Remove file – cache should still say True
        f.unlink()
        assert CachedExists.exists(str(f)) is True

    def test_handles_nonexistent_directory(self, tmp_path):
        bad = str(tmp_path / "no_such_dir" / "file.txt")
        assert CachedExists.exists(bad) is False

    def test_handles_empty_filename(self):
        # e.g. path = "/" or similar edge case
        result = CachedExists.exists("/")
        assert isinstance(result, bool)

    def test_handles_path_normalization(self, tmp_path):
        f = tmp_path / "norm.txt"
        f.write_text("data")
        # Add redundant separators
        weird_path = str(tmp_path) + "//norm.txt"
        assert CachedExists.exists(weird_path) is True


class TestInvalidation:

    def test_invalidate_dir_removes_cache(self, tmp_path):
        f = tmp_path / "inv.txt"
        f.write_text("data")
        assert CachedExists.exists(str(f)) is True

        # Invalidate
        CachedExists.invalidate_dir(str(tmp_path))
        # Now remove the file
        f.unlink()
        assert CachedExists.exists(str(f)) is False

    def test_clear_removes_all_caches(self, tmp_path):
        f1 = tmp_path / "a.txt"
        f1.write_text("a")
        sub = tmp_path / "sub"
        sub.mkdir()
        f2 = sub / "b.txt"
        f2.write_text("b")

        CachedExists.exists(str(f1))
        CachedExists.exists(str(f2))
        assert len(CachedExists._dir_cache) == 2

        CachedExists.clear()
        assert len(CachedExists._dir_cache) == 0
