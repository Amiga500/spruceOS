"""Tests for mainui argument parsing and device initialization logic.

These tests require the ``sdl2`` native library which is only available on
target devices.  The entire module is skipped when ``sdl2`` cannot be
imported so that the rest of the test suite runs cleanly in CI.
"""

import sys

import pytest

# mainui.py transitively imports sdl2 (a native library that is only
# available on the target device).  Skip the whole module when it is absent.
sdl2 = pytest.importorskip("sdl2", reason="sdl2 not available in test environment")


class TestParseArguments:
    """Test the argument parser defined in mainui.py."""

    def test_defaults(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["mainui.py"])
        from mainui import parse_arguments

        args = parse_arguments()
        assert args.logDir == "/mnt/SDCARD/pyui/logs/"
        assert args.device == "MIYOO_FLIP"
        assert args.cfwConfig is None
        assert args.msgDisplay is None

    def test_custom_device(self, monkeypatch):
        monkeypatch.setattr(
            sys, "argv", ["mainui.py", "-device", "TRIMUI_BRICK"]
        )
        from mainui import parse_arguments

        args = parse_arguments()
        assert args.device == "TRIMUI_BRICK"

    def test_custom_log_dir(self, monkeypatch):
        monkeypatch.setattr(
            sys, "argv", ["mainui.py", "-logDir", "/tmp/logs"]
        )
        from mainui import parse_arguments

        args = parse_arguments()
        assert args.logDir == "/tmp/logs"

    def test_msg_display(self, monkeypatch):
        monkeypatch.setattr(
            sys,
            "argv",
            ["mainui.py", "-msgDisplay", "Hello", "-msgDisplayTimeMs", "3000"],
        )
        from mainui import parse_arguments

        args = parse_arguments()
        assert args.msgDisplay == "Hello"
        assert args.msgDisplayTimeMs == "3000"

    def test_option_list_file(self, monkeypatch):
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "mainui.py",
                "-optionListFile",
                "/tmp/opts.json",
                "-optionListTitle",
                "Pick One",
            ],
        )
        from mainui import parse_arguments

        args = parse_arguments()
        assert args.optionListFile == "/tmp/opts.json"
        assert args.optionListTitle == "Pick One"


class TestInitializeDevice:
    """Test the device factory function."""

    def test_unsupported_device_raises(self, monkeypatch):
        from mainui import initialize_device

        with pytest.raises(RuntimeError, match="not a supported device"):
            initialize_device("UNSUPPORTED_DEVICE_XYZ", True)
