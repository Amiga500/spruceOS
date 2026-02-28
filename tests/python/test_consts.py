"""Tests for utils.consts module constants."""

from utils.consts import (
    COLLECTIONS,
    FAVORITES,
    GAME_SELECT,
    GAME_SWITCHER,
    RECENTS,
)


class TestConstants:
    """Verify that constants have the expected values and types."""

    def test_collections(self):
        assert COLLECTIONS == "Collections"

    def test_favorites(self):
        assert FAVORITES == "Favorites"

    def test_game_select(self):
        assert GAME_SELECT == "GameSelect"

    def test_recents(self):
        assert RECENTS == "Recents"

    def test_game_switcher(self):
        assert GAME_SWITCHER == "GameSwitcher"

    def test_all_are_strings(self):
        for const in (COLLECTIONS, FAVORITES, GAME_SELECT, RECENTS, GAME_SWITCHER):
            assert isinstance(const, str)

    def test_no_duplicates(self):
        values = [COLLECTIONS, FAVORITES, GAME_SELECT, RECENTS, GAME_SWITCHER]
        assert len(values) == len(set(values))
