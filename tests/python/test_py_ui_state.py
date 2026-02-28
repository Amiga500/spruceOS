"""Tests for utils.py_ui_state.PyUiState."""

import json

import pytest

from utils.py_ui_state import PyUiState


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _reset_state():
    PyUiState._data = {}
    PyUiState._config_path = None


@pytest.fixture(autouse=True)
def reset():
    _reset_state()
    yield
    _reset_state()


# ---------------------------------------------------------------------------
# Initialization & persistence
# ---------------------------------------------------------------------------


class TestInitAndPersistence:

    def test_init_with_initial_data(self, tmp_dir):
        path = str(tmp_dir / "state.json")
        PyUiState.init(path, initial_data={"key": "val"})
        # init calls load(), which will overwrite; but if file doesn't exist it
        # falls back to {}. We check the file was created by save() in setters.
        assert PyUiState._config_path == path

    def test_save_and_load_round_trip(self, tmp_dir):
        path = str(tmp_dir / "state.json")
        PyUiState.init(path, initial_data={})
        PyUiState.set("x", 123)
        PyUiState.save()

        # Re-init to read from disk
        _reset_state()
        PyUiState.init(path)
        assert PyUiState.get("x") == 123

    def test_load_missing_file(self, tmp_dir):
        path = str(tmp_dir / "missing.json")
        PyUiState._config_path = path
        PyUiState.load()
        assert PyUiState._data == {}

    def test_load_corrupt_file(self, tmp_dir):
        path = tmp_dir / "bad.json"
        path.write_text("not json{{{")
        PyUiState._config_path = str(path)
        PyUiState.load()
        assert PyUiState._data == {}

    def test_clear_resets_data(self, tmp_dir):
        path = str(tmp_dir / "state.json")
        PyUiState.init(path, initial_data={})
        PyUiState.set("a", 1)
        PyUiState.save()
        PyUiState.clear()
        assert PyUiState._data == {}
        data = json.loads((tmp_dir / "state.json").read_text())
        assert data == {}


# ---------------------------------------------------------------------------
# Domain-specific getters/setters
# ---------------------------------------------------------------------------


class TestDomainAccessors:

    def test_last_system_selection(self, tmp_dir):
        path = str(tmp_dir / "state.json")
        PyUiState.init(path, initial_data={})
        assert PyUiState.get_last_system_selection() is None
        PyUiState.set_last_system_selection("NES")
        assert PyUiState.get_last_system_selection() == "NES"

    def test_last_app_selection(self, tmp_dir):
        path = str(tmp_dir / "state.json")
        PyUiState.init(path, initial_data={})
        assert PyUiState.get_last_app_selection() is None
        PyUiState.set_last_app_selection("RetroArch")
        assert PyUiState.get_last_app_selection() == "RetroArch"

    def test_last_game_selection(self, tmp_dir):
        path = str(tmp_dir / "state.json")
        PyUiState.init(path, initial_data={})
        game, subfolder = PyUiState.get_last_game_selection("SNES")
        assert game is None
        assert subfolder is None

        PyUiState.set_last_game_selection("SNES", "SuperMarioWorld.sfc", "platformers")
        game, subfolder = PyUiState.get_last_game_selection("SNES")
        assert game == "SuperMarioWorld.sfc"
        assert subfolder == "platformers"

    def test_in_game_selection_screen(self, tmp_dir):
        path = str(tmp_dir / "state.json")
        PyUiState.init(path, initial_data={})
        assert PyUiState.get_in_game_selection_screen() is False
        PyUiState.set_in_game_selection_screen(True)
        assert PyUiState.get_in_game_selection_screen() is True

    def test_last_main_menu_selection(self, tmp_dir):
        path = str(tmp_dir / "state.json")
        PyUiState.init(path, initial_data={})
        assert PyUiState.get_last_main_menu_selection() is None
        PyUiState.set_last_main_menu_selection("Games")
        assert PyUiState.get_last_main_menu_selection() == "Games"

    def test_contains(self, tmp_dir):
        path = str(tmp_dir / "state.json")
        PyUiState.init(path, initial_data={})
        PyUiState.set("present", True)
        assert PyUiState.__contains__("present") is True
        assert PyUiState.__contains__("absent") is False
