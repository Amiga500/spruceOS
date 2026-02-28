"""Tests for utils.py_ui_config.PyUiConfig."""

import json

import pytest

from utils.py_ui_config import PyUiConfig


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _reset_config():
    """Reset the class-level singleton state between tests."""
    PyUiConfig._data = {}
    PyUiConfig._config_path = None


@pytest.fixture(autouse=True)
def reset(tmp_dir):
    _reset_config()
    yield
    _reset_config()


# ---------------------------------------------------------------------------
# Initialization & persistence
# ---------------------------------------------------------------------------


class TestInitAndPersistence:
    """Init, load, save round-trip."""

    def test_init_with_missing_file_uses_defaults(self, tmp_dir):
        path = str(tmp_dir / "cfg.json")
        PyUiConfig.init(path, initial_data={"key": "value"})
        # init() calls load() which finds no file, so _data is reset to {}
        assert PyUiConfig._data == {}

    def test_init_loads_existing_file(self, tmp_json_file):
        path = tmp_json_file({"turboDelayMs": 200})
        PyUiConfig.init(str(path))
        assert PyUiConfig.get("turboDelayMs") == 200

    def test_save_persists_to_disk(self, tmp_dir):
        path = str(tmp_dir / "cfg.json")
        PyUiConfig.init(path, initial_data={"a": 1})
        PyUiConfig.set("a", 42)
        PyUiConfig.save()
        data = json.loads((tmp_dir / "cfg.json").read_text())
        assert data["a"] == 42

    def test_load_handles_missing_file(self, tmp_dir):
        path = str(tmp_dir / "nonexistent.json")
        PyUiConfig._config_path = path
        PyUiConfig.load()
        assert PyUiConfig._data == {}

    def test_load_handles_corrupt_json(self, tmp_dir):
        path = tmp_dir / "bad.json"
        path.write_text("{invalid json")
        PyUiConfig._config_path = str(path)
        PyUiConfig.load()
        assert PyUiConfig._data == {}


# ---------------------------------------------------------------------------
# Getters & setters
# ---------------------------------------------------------------------------


class TestGettersAndSetters:
    """Verify dictionary-like access and domain-specific getters/setters."""

    def test_get_returns_default_when_key_missing(self, tmp_dir):
        PyUiConfig.init(str(tmp_dir / "cfg.json"), initial_data={})
        assert PyUiConfig.get("missing", "fallback") == "fallback"

    def test_set_and_get(self, tmp_dir):
        PyUiConfig.init(str(tmp_dir / "cfg.json"), initial_data={})
        PyUiConfig.set("foo", "bar")
        assert PyUiConfig.get("foo") == "bar"

    def test_contains(self, tmp_json_file):
        path = tmp_json_file({"x": 1})
        PyUiConfig.init(str(path))
        assert PyUiConfig.__contains__("x") is True
        assert PyUiConfig.__contains__("y") is False

    def test_to_dict_returns_copy(self, tmp_json_file):
        path = tmp_json_file({"a": 1})
        PyUiConfig.init(str(path))
        d = PyUiConfig.to_dict()
        d["a"] = 999
        assert PyUiConfig.get("a") == 1  # original unchanged

    def test_clear(self, tmp_dir):
        PyUiConfig.init(str(tmp_dir / "cfg.json"), initial_data={"a": 1})
        PyUiConfig.clear()
        assert PyUiConfig._data == {}


# ---------------------------------------------------------------------------
# Domain-specific properties
# ---------------------------------------------------------------------------


class TestDomainProperties:
    """Test the convenience accessors for specific config keys."""

    def test_get_turbo_delay_ms_default(self, tmp_dir):
        PyUiConfig.init(str(tmp_dir / "cfg.json"), initial_data={})
        # default is 120 / 1000 = 0.12
        assert PyUiConfig.get_turbo_delay_ms() == pytest.approx(0.12)

    def test_set_turbo_delay_ms(self, tmp_dir):
        PyUiConfig.init(str(tmp_dir / "cfg.json"), initial_data={})
        PyUiConfig.set_turbo_delay_ms(300)
        assert PyUiConfig.get_turbo_delay_ms() == pytest.approx(0.3)

    def test_enable_button_watchers_default(self, tmp_dir):
        PyUiConfig.init(str(tmp_dir / "cfg.json"), initial_data={})
        assert PyUiConfig.enable_button_watchers() is True

    def test_enable_wifi_monitor_default(self, tmp_dir):
        PyUiConfig.init(str(tmp_dir / "cfg.json"), initial_data={})
        assert PyUiConfig.enable_wifi_monitor() is True

    def test_get_main_menu_title_default(self, tmp_dir):
        PyUiConfig.init(str(tmp_dir / "cfg.json"), initial_data={})
        assert PyUiConfig.get_main_menu_title() == "PyUI"

    def test_get_cfw_name_default(self, tmp_dir):
        PyUiConfig.init(str(tmp_dir / "cfg.json"), initial_data={})
        assert PyUiConfig.get_cfw_name() == "CFW"

    def test_use_24_hour_clock_default(self, tmp_dir):
        PyUiConfig.init(str(tmp_dir / "cfg.json"), initial_data={})
        assert PyUiConfig.use_24_hour_clock() is False

    def test_set_use_24_hour_clock(self, tmp_dir):
        PyUiConfig.init(str(tmp_dir / "cfg.json"), initial_data={})
        PyUiConfig.set_use_24_hour_clock(True)
        assert PyUiConfig.use_24_hour_clock() is True

    def test_show_all_game_systems_default(self, tmp_dir):
        PyUiConfig.init(str(tmp_dir / "cfg.json"), initial_data={})
        assert PyUiConfig.show_all_game_systems() is False

    def test_show_am_pm_default(self, tmp_dir):
        PyUiConfig.init(str(tmp_dir / "cfg.json"), initial_data={})
        assert PyUiConfig.show_am_pm() is True

    def test_game_system_sort_mode_default(self, tmp_dir):
        PyUiConfig.init(str(tmp_dir / "cfg.json"), initial_data={})
        assert PyUiConfig.game_system_sort_mode() == "Alphabetical"

    def test_get_language_default(self, tmp_dir):
        PyUiConfig.init(str(tmp_dir / "cfg.json"), initial_data={})
        assert PyUiConfig.get_language() == "English"

    def test_set_language(self, tmp_dir):
        PyUiConfig.init(str(tmp_dir / "cfg.json"), initial_data={})
        PyUiConfig.set_language("Italian")
        assert PyUiConfig.get_language() == "Italian"

    def test_include_stock_os_launch_option_default(self, tmp_dir):
        PyUiConfig.init(str(tmp_dir / "cfg.json"), initial_data={})
        assert PyUiConfig.include_stock_os_launch_option() is True

    def test_allow_pyui_game_switcher_default(self, tmp_dir):
        PyUiConfig.init(str(tmp_dir / "cfg.json"), initial_data={})
        assert PyUiConfig.allow_pyui_game_switcher() is True

    def test_get_gameswitcher_path_default(self, tmp_dir):
        PyUiConfig.init(str(tmp_dir / "cfg.json"), initial_data={})
        assert PyUiConfig.get_gameswitcher_path() is None

    def test_cfw_tasks_json_default(self, tmp_dir):
        PyUiConfig.init(str(tmp_dir / "cfg.json"), initial_data={})
        assert PyUiConfig.cfw_tasks_json() is None

    def test_game_system_sort_priorities(self, tmp_dir):
        PyUiConfig.init(str(tmp_dir / "cfg.json"), initial_data={})
        assert PyUiConfig.game_system_sort_type_priority() == 1
        assert PyUiConfig.game_system_sort_brand_priority() == 2
        assert PyUiConfig.game_system_sort_year_priority() == 3
        assert PyUiConfig.game_system_sort_name_priority() == 4

    def test_set_game_system_sort_type_priority(self, tmp_dir):
        PyUiConfig.init(str(tmp_dir / "cfg.json"), initial_data={})
        PyUiConfig.set_game_system_sort_type_priority(5)
        assert PyUiConfig.game_system_sort_type_priority() == 5

    def test_get_wpa_supplicant_conf_file_location(self, tmp_dir):
        PyUiConfig.init(str(tmp_dir / "cfg.json"), initial_data={})
        assert PyUiConfig.get_wpa_supplicant_conf_file_location("/default") == "/default"

    def test_get_activity_log_path_default(self, tmp_dir):
        PyUiConfig.init(str(tmp_dir / "cfg.json"), initial_data={})
        assert PyUiConfig.get_activity_log_path() is None
