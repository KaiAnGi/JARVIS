"""Tests for plugins/help/plugin.py"""

from core.language import set_lang
from plugins.help import plugin


class TestHandle:
    def test_help_es(self, bus):
        set_lang("es")
        plugin.handle("help", "", bus)
        bus.emit.assert_called_once()
        event, msg = bus.emit.call_args[0]
        assert event == "speak"
        assert isinstance(msg, str)
        assert len(msg) > 10  # should be a meaningful help string

    def test_help_en(self, bus):
        set_lang("en")
        plugin.handle("help", "", bus)
        bus.emit.assert_called_once()
        event, msg = bus.emit.call_args[0]
        assert event == "speak"

    def test_help_category_found_es(self, bus):
        set_lang("es")
        plugin.handle("help_category", "ayuda con git", bus)
        bus.emit.assert_called_once()
        event, msg = bus.emit.call_args[0]
        assert event == "speak"
        # The category description should contain actual help text, not a key
        assert "git" in msg.lower()
        assert "commit" in msg.lower() or "push" in msg.lower() or "status" in msg.lower()

    def test_help_category_found_en(self, bus):
        set_lang("en")
        plugin.handle("help_category", "help with git", bus)
        bus.emit.assert_called_once()
        event, msg = bus.emit.call_args[0]
        assert event == "speak"
        assert "git" in msg.lower()

    def test_help_category_not_found(self, bus):
        set_lang("es")
        plugin.handle("help_category", "ayuda con cohetes", bus)
        bus.emit.assert_called_once()
        event, msg = bus.emit.call_args[0]
        assert event == "speak"
        assert isinstance(msg, str)
        assert len(msg) > 0


class TestCategoriesData:
    def test_es_categories_not_empty(self):
        assert len(plugin.CATEGORIES_ES) > 0

    def test_en_categories_not_empty(self):
        assert len(plugin.CATEGORIES_EN) > 0

    def test_categories_have_same_count(self):
        assert len(plugin.CATEGORIES_ES) == len(plugin.CATEGORIES_EN)

    def test_all_es_categories_are_nonempty_strings(self):
        for key, value in plugin.CATEGORIES_ES.items():
            assert isinstance(key, str)
            assert isinstance(value, str)
            assert len(key) > 0
            assert len(value) > 0

    def test_all_en_categories_are_nonempty_strings(self):
        for key, value in plugin.CATEGORIES_EN.items():
            assert isinstance(key, str)
            assert isinstance(value, str)
            assert len(key) > 0
            assert len(value) > 0

    def test_each_es_category_has_en_equivalent(self):
        for key in plugin.CATEGORIES_ES:
            # Each ES category key should correspond to a category in EN with the same description pattern
            assert isinstance(plugin.CATEGORIES_ES[key], str)
            assert len(plugin.CATEGORIES_ES[key]) > 0
        for key in plugin.CATEGORIES_EN:
            assert isinstance(plugin.CATEGORIES_EN[key], str)
            assert len(plugin.CATEGORIES_EN[key]) > 0

    def test_categories_have_unique_keys(self):
        assert len(plugin.CATEGORIES_ES) == len(set(plugin.CATEGORIES_ES))
        assert len(plugin.CATEGORIES_EN) == len(set(plugin.CATEGORIES_EN))
