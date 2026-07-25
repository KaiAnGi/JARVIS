"""Tests for core/intent_router.py"""

from unittest.mock import MagicMock

from core.intent_router import IntentRouter
from core.language import set_lang


class TestIntentRouter:
    def _make_module(self, name="test"):
        mod = MagicMock()
        mod.__name__ = name
        return mod

    def test_register_and_route(self):
        set_lang("en")
        router = IntentRouter()
        bus = MagicMock()
        mod = self._make_module()
        router.register_plugin("browser", mod)
        router.rebuild_patterns()

        result = router.route("search for cats", bus)
        assert result is True
        mod.handle.assert_called_once()

    def test_route_no_match(self):
        set_lang("en")
        router = IntentRouter()
        bus = MagicMock()
        router.rebuild_patterns()
        assert router.route("xyzabc123", bus) is False

    def test_longest_pattern_wins(self):
        set_lang("en")
        router = IntentRouter()
        bus = MagicMock()
        mod = self._make_module()
        router.register_plugin("browser", mod)
        router.rebuild_patterns()

        # "play on youtube" is longer than "play"
        router.route("play on youtube cats", bus)
        call_args = mod.handle.call_args
        assert call_args[0][0] == "youtube_play"

    def test_rebuild_patterns_after_lang_change(self):
        router = IntentRouter()
        bus = MagicMock()
        mod = self._make_module()
        router.register_plugin("help", mod)
        router.rebuild_patterns()

        # Spanish
        set_lang("es")
        router.rebuild_patterns()
        router.route("ayuda", bus)
        assert mod.handle.call_args[0][0] == "help"

        mod.reset_mock()
        # English
        set_lang("en")
        router.rebuild_patterns()
        router.route("help", bus)
        assert mod.handle.call_args[0][0] == "help"

    def test_multiple_plugins_no_conflict(self):
        set_lang("es")
        router = IntentRouter()
        bus = MagicMock()
        mod1 = self._make_module("browser")
        mod2 = self._make_module("datetime_calc")
        router.register_plugin("browser", mod1)
        router.register_plugin("datetime_calc", mod2)
        router.rebuild_patterns()

        router.route("qué hora es", bus)
        mod2.handle.assert_called_once()
        mod1.handle.assert_not_called()
