"""Tests for utils.cfw_system_config.CfwSystemConfig."""

import json

import pytest

from utils.cfw_system_config import CfwSystemConfig


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SAMPLE_CONFIG = {
    "menuOptions": {
        "Display": {
            "brightness": {
                "selected": "5",
                "options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
            },
            "contrast": {
                "selected": "50",
                "options": ["0", "25", "50", "75", "100"],
            },
        },
        "Audio": {
            "volume": {
                "selected": "80",
                "options": ["0", "20", "40", "60", "80", "100"],
            }
        },
    }
}


def _reset():
    CfwSystemConfig._data = {}
    CfwSystemConfig._config_path = None


@pytest.fixture(autouse=True)
def reset():
    _reset()
    yield
    _reset()


# ---------------------------------------------------------------------------
# Init & reload
# ---------------------------------------------------------------------------


class TestInitAndReload:

    def test_init_loads_file(self, tmp_json_file):
        path = tmp_json_file(SAMPLE_CONFIG, "cfw.json")
        CfwSystemConfig.init(str(path))
        assert CfwSystemConfig._data == SAMPLE_CONFIG

    def test_init_with_missing_file(self, tmp_dir):
        CfwSystemConfig.init(str(tmp_dir / "missing.json"))
        assert CfwSystemConfig._data == {}

    def test_init_with_none_path(self):
        CfwSystemConfig.init(None)
        assert CfwSystemConfig._data == {}

    def test_reload_picks_up_changes(self, tmp_json_file):
        path = tmp_json_file(SAMPLE_CONFIG, "cfw.json")
        CfwSystemConfig.init(str(path))
        # Modify the file externally
        updated = {**SAMPLE_CONFIG, "extra": True}
        path.write_text(json.dumps(updated))
        CfwSystemConfig.reload_config()
        assert CfwSystemConfig._data.get("extra") is True


# ---------------------------------------------------------------------------
# Category / menu option accessors
# ---------------------------------------------------------------------------


class TestMenuAccessors:

    def test_get_categories(self, tmp_json_file):
        path = tmp_json_file(SAMPLE_CONFIG, "cfw.json")
        CfwSystemConfig.init(str(path))
        cats = CfwSystemConfig.get_categories()
        assert set(cats) == {"Display", "Audio"}

    def test_get_menu_options_with_category(self, tmp_json_file):
        path = tmp_json_file(SAMPLE_CONFIG, "cfw.json")
        CfwSystemConfig.init(str(path))
        opts = CfwSystemConfig.get_menu_options("Display")
        assert "brightness" in opts
        assert "contrast" in opts

    def test_get_menu_options_unknown_category(self, tmp_json_file):
        path = tmp_json_file(SAMPLE_CONFIG, "cfw.json")
        CfwSystemConfig.init(str(path))
        assert CfwSystemConfig.get_menu_options("Unknown") == {}

    def test_get_menu_options_no_category(self, tmp_json_file):
        path = tmp_json_file(SAMPLE_CONFIG, "cfw.json")
        CfwSystemConfig.init(str(path))
        all_opts = CfwSystemConfig.get_menu_options(None)
        assert "Display" in all_opts
        assert "Audio" in all_opts

    def test_get_menu_option(self, tmp_json_file):
        path = tmp_json_file(SAMPLE_CONFIG, "cfw.json")
        CfwSystemConfig.init(str(path))
        opt = CfwSystemConfig.get_menu_option("Audio", "volume")
        assert opt["selected"] == "80"

    def test_get_menu_option_not_found(self, tmp_json_file):
        path = tmp_json_file(SAMPLE_CONFIG, "cfw.json")
        CfwSystemConfig.init(str(path))
        assert CfwSystemConfig.get_menu_option("Audio", "bass") is None

    def test_get_selected_value(self, tmp_json_file):
        path = tmp_json_file(SAMPLE_CONFIG, "cfw.json")
        CfwSystemConfig.init(str(path))
        assert CfwSystemConfig.get_selected_value("Display", "brightness") == "5"

    def test_get_selected_value_missing(self, tmp_json_file):
        path = tmp_json_file(SAMPLE_CONFIG, "cfw.json")
        CfwSystemConfig.init(str(path))
        assert CfwSystemConfig.get_selected_value("Display", "gamma") is None


# ---------------------------------------------------------------------------
# set_menu_option
# ---------------------------------------------------------------------------


class TestSetMenuOption:

    def test_set_menu_option_updates_selected(self, tmp_json_file):
        path = tmp_json_file(SAMPLE_CONFIG, "cfw.json")
        CfwSystemConfig.init(str(path))
        CfwSystemConfig.set_menu_option("Display", "brightness", "10")
        assert CfwSystemConfig.get_selected_value("Display", "brightness") == "10"

    def test_set_menu_option_persists_to_file(self, tmp_json_file):
        path = tmp_json_file(SAMPLE_CONFIG, "cfw.json")
        CfwSystemConfig.init(str(path))
        CfwSystemConfig.set_menu_option("Audio", "volume", "100")
        data = json.loads(path.read_text())
        assert data["menuOptions"]["Audio"]["volume"]["selected"] == "100"

    def test_set_menu_option_nonexistent_option(self, tmp_json_file):
        path = tmp_json_file(SAMPLE_CONFIG, "cfw.json")
        CfwSystemConfig.init(str(path))
        # Should be a no-op (no crash)
        CfwSystemConfig.set_menu_option("Display", "nonexistent", "42")
        assert CfwSystemConfig.get_menu_option("Display", "nonexistent") is None
