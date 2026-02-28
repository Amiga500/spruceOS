"""Tests for ExtensionPreservingRotatingFileHandler.

Note: the source module is named ``etension_preserving_rotating_file_handler``
(typo in the original codebase).
"""

import logging
import os

import pytest

from utils.etension_preserving_rotating_file_handler import (
    ExtensionPreservingRotatingFileHandler,
)


class TestDoRollover:
    """Verify the log rotation preserves the .log extension."""

    def test_rollover_creates_numbered_backups(self, tmp_path):
        log_file = str(tmp_path / "app.log")
        handler = ExtensionPreservingRotatingFileHandler(
            log_file, maxBytes=50, backupCount=3
        )
        logger = logging.getLogger("test_rollover")
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        # Write enough to trigger multiple rollovers
        for i in range(20):
            logger.debug(f"Log line number {i:04d}")

        handler.close()
        logger.removeHandler(handler)

        # Check that backup files have correct naming pattern
        assert os.path.exists(str(tmp_path / "app.1.log"))

    def test_rollover_respects_backup_count(self, tmp_path):
        log_file = str(tmp_path / "test.log")
        handler = ExtensionPreservingRotatingFileHandler(
            log_file, maxBytes=30, backupCount=2
        )
        logger = logging.getLogger("test_backup_count")
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        for i in range(30):
            logger.debug(f"Message {i:05d}")

        handler.close()
        logger.removeHandler(handler)

        # Should NOT have .3.log with backupCount=2
        assert not os.path.exists(str(tmp_path / "test.3.log"))

    def test_rollover_preserves_extension(self, tmp_path):
        log_file = str(tmp_path / "myapp.log")
        handler = ExtensionPreservingRotatingFileHandler(
            log_file, maxBytes=50, backupCount=2
        )
        logger = logging.getLogger("test_ext_preserve")
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        for i in range(15):
            logger.debug(f"Line {i}")

        handler.close()
        logger.removeHandler(handler)

        files = os.listdir(tmp_path)
        for f in files:
            assert f.endswith(".log"), f"File {f} does not end with .log"
