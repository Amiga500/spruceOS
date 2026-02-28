"""Tests for utils.config_copier.ConfigCopier."""

from pathlib import Path

import pytest

from utils.config_copier import ConfigCopier


class TestEnsureConfig:

    def test_copies_when_destination_missing(self, tmp_path):
        src = tmp_path / "source" / "config.json"
        src.parent.mkdir(parents=True, exist_ok=True)
        src.write_text('{"key": "value"}')

        dest = tmp_path / "dest" / "config.json"
        ConfigCopier.ensure_config(str(dest), src)

        assert dest.exists()
        assert dest.read_text() == '{"key": "value"}'

    def test_does_not_overwrite_existing(self, tmp_path):
        src = tmp_path / "source" / "config.json"
        src.parent.mkdir(parents=True, exist_ok=True)
        src.write_text('{"new": true}')

        dest = tmp_path / "dest" / "config.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text('{"old": true}')

        ConfigCopier.ensure_config(str(dest), src)

        assert dest.read_text() == '{"old": true}'

    def test_overwrites_empty_file(self, tmp_path):
        src = tmp_path / "source" / "config.json"
        src.parent.mkdir(parents=True, exist_ok=True)
        src.write_text('{"default": true}')

        dest = tmp_path / "dest" / "config.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text("")  # empty file

        ConfigCopier.ensure_config(str(dest), src)

        assert dest.read_text() == '{"default": true}'

    def test_creates_parent_directories(self, tmp_path):
        src = tmp_path / "config.json"
        src.write_text('{"a": 1}')

        dest = tmp_path / "deep" / "nested" / "dir" / "config.json"
        ConfigCopier.ensure_config(str(dest), src)

        assert dest.exists()

    def test_handles_missing_source_gracefully(self, tmp_path):
        src = Path(str(tmp_path / "nonexistent" / "config.json"))
        dest = tmp_path / "dest" / "config.json"

        # Should not raise; logs the error instead
        ConfigCopier.ensure_config(str(dest), src)
        assert not dest.exists()
