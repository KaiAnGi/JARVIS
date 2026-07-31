"""Tests for core/fuzzy_actions.py and core/command_processor.py"""

from unittest.mock import patch

from core import command_processor, fuzzy_actions, fuzzy_intent


class FakePlugin:
    """Stands in for a plugin module: records (action, text, bus) calls."""

    def __init__(self):
        self.calls = []
        self.waiting = False

    def handle(self, action, text, bus):
        self.calls.append((action, text, bus))


class FakeRouter:
    def __init__(self):
        self.plugins = {}

    def get_plugin(self, name):
        return self.plugins.get(name)


def _make_router(*names):
    router = FakeRouter()
    for name in names:
        router.plugins[name] = FakePlugin()
    return router


class TestExecuteFuzzyAction:
    def test_plugin_action_dispatches(self, bus):
        router = _make_router("system_control")
        fuzzy_actions.execute_fuzzy_action({"action": "open_app", "app": "notepad"}, router, bus)
        assert router.plugins["system_control"].calls == [("open_app", "open notepad", bus)]

    def test_unknown_plugin_emits_no_match(self, bus):
        router = _make_router()
        handled = fuzzy_actions.execute_fuzzy_action({"action": "bogus_plugin", "extra": 1}, router, bus)
        assert handled is False
        assert bus._events == [("speak", fuzzy_actions.resp("no_match"))]

    def test_unknown_action_emits_no_match(self, bus):
        router = _make_router("system_control")
        handled = fuzzy_actions.execute_fuzzy_action({"action": "drop_database"}, router, bus)
        assert handled is False
        assert router.plugins["system_control"].calls == []
        assert bus._events == [("speak", fuzzy_actions.resp("no_match"))]

    def test_static_text_action_emits_speak(self, bus):
        router = _make_router("help")
        handled = fuzzy_actions.execute_fuzzy_action({"action": "help"}, router, bus)
        assert handled is True
        assert router.plugins["help"].calls == [("help", "help", bus)]

    def test_build_alarm_text(self):
        text = fuzzy_actions._build_alarm_text({"action": "set_alarm", "time": "09:00"})
        assert "09:00" in text


class TestProcessUnmatched:
    def test_not_ready_emits_no_ollama(self, bus):
        router = _make_router()
        with patch.object(fuzzy_intent, "is_ollama_ready", return_value=False):
            handled = command_processor.process_unmatched("algo", router, bus)
        assert handled is False
        assert bus._events == [("speak", fuzzy_actions.resp("no_ollama"))]

    def test_no_intent_emits_no_match(self, bus):
        router = _make_router()
        with (
            patch.object(fuzzy_intent, "is_ollama_ready", return_value=True),
            patch.object(fuzzy_intent, "match_fuzzy", return_value=None),
        ):
            handled = command_processor.process_unmatched("algo", router, bus)
        assert handled is False
        assert bus._events == [("speak", fuzzy_actions.resp("no_match"))]

    def test_ollama_dispatches_plugin_action(self, bus):
        router = _make_router("system_control")
        intent = {"action": "open_app", "app": "notepad"}
        with (
            patch.object(fuzzy_intent, "is_ollama_ready", return_value=True),
            patch.object(fuzzy_intent, "match_fuzzy", return_value=intent),
        ):
            handled = command_processor.process_unmatched("abre el notepad", router, bus)
        assert handled is True
        assert router.plugins["system_control"].calls == [("open_app", "open notepad", bus)]
