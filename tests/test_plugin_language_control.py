"""Tests for plugins/language_control/plugin.py"""

from core.language import get_lang, set_lang
from plugins.language_control import plugin


class TestHandle:
    def test_toggle_es_to_en(self, bus):
        set_lang("es")
        plugin.handle("toggle_language", "", bus)
        assert get_lang() == "en"

    def test_toggle_en_to_es(self, bus):
        set_lang("en")
        plugin.handle("toggle_language", "", bus)
        assert get_lang() == "es"

    def test_set_spanish(self, bus):
        set_lang("en")
        plugin.handle("set_spanish", "", bus)
        assert get_lang() == "es"

    def test_set_spanish_already_es(self, bus):
        set_lang("es")
        plugin.handle("set_spanish", "", bus)
        assert get_lang() == "es"

    def test_set_english(self, bus):
        set_lang("es")
        plugin.handle("set_english", "", bus)
        assert get_lang() == "en"

    def test_set_english_already_en(self, bus):
        set_lang("en")
        plugin.handle("set_english", "", bus)
        assert get_lang() == "en"

    def test_toggle_emits_language_changed(self, bus):
        plugin.handle("toggle_language", "", bus)
        bus.emit.assert_any_call("language_changed", get_lang())
