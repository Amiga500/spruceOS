"""
Pytest configuration and shared fixtures for PyUI tests.

Adds the main-ui source directory to sys.path and provides common
fixtures (temporary directories, mock logger, etc.) used across test
modules.
"""

import json
import logging
import os
import sys
import tempfile

import pytest

# ---------------------------------------------------------------------------
# Make the PyUI source importable
# ---------------------------------------------------------------------------
MAIN_UI_DIR = os.path.join(
    os.path.dirname(__file__),
    os.pardir,
    os.pardir,
    "App",
    "PyUI",
    "main-ui",
)
sys.path.insert(0, os.path.abspath(MAIN_UI_DIR))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_dir(tmp_path):
    """Provide a clean temporary directory path."""
    return tmp_path


@pytest.fixture
def tmp_json_file(tmp_path):
    """Create a temporary JSON file with the given data.

    Returns a factory function: call ``tmp_json_file(data)`` to get a
    ``pathlib.Path`` pointing to the written file.
    """

    def _create(data: dict, filename: str = "config.json"):
        path = tmp_path / filename
        path.write_text(json.dumps(data, indent=4))
        return path

    return _create


@pytest.fixture(autouse=True)
def mock_logger(monkeypatch):
    """Ensure PyUiLogger.get_logger() returns a standard logger.

    This avoids the need for the full PyUiLogger.init() call and prevents
    any file I/O side‑effects from logging during tests.
    """
    logger = logging.getLogger("test_pyui")
    logger.setLevel(logging.DEBUG)

    # Lazy‑import so the path fixup above takes effect first.
    from utils.logger import PyUiLogger

    monkeypatch.setattr(PyUiLogger, "_logger", logger)
    return logger
