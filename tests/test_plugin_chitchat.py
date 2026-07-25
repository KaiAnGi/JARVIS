"""Tests for plugins/chitchat/plugin.py"""

from unittest.mock import patch
from datetime import datetime

from core.language import set_lang
from plugins.chitchat import plugin


class TestGreeting:
    def test_morning_es(self):
        result = plugin._greeting("es", 8)
        assert "buenos días" in result.lower()

    def test_afternoon_es(self):
        result = plugin._greeting("es", 14)
        assert "buenas tardes" in result.lower()

    def test_evening_es(self):
        result = plugin._greeting("es", 21)
        assert "buenas noches" in result.lower()

    def test_morning_en(self):
        result = plugin._greeting("en", 8)
        assert "morning" in result.lower()

    def test_afternoon_en(self):
        result = plugin._greeting("en", 14)
        assert "afternoon" in result.lower()

    def test_evening_en(self):
        result = plugin._greeting("en", 21)
        assert "evening" in result.lower()

    def test_greeting_es_is_nonempty(self):
        result = plugin._greeting("es", 10)
        assert isinstance(result, str)
        assert len(result) > 5

    def test_greeting_en_is_nonempty(self):
        result = plugin._greeting("en", 10)
        assert isinstance(result, str)
        assert len(result) > 5


class TestResponses:
    def test_how_are_you_es(self):
        result = plugin._how_are_you("es")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_how_are_you_en(self):
        result = plugin._how_are_you("en")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_who_are_you_es(self):
        result = plugin._who_are_you("es")
        assert "j.a.r.v.i.s." in result.lower()

    def test_who_are_you_en(self):
        result = plugin._who_are_you("en")
        assert "j.a.r.v.i.s." in result.lower()

    def test_thanks_es(self):
        result = plugin._thanks("es")
        assert isinstance(result, str)
        assert len(result) > 5

    def test_thanks_en(self):
        result = plugin._thanks("en")
        assert isinstance(result, str)
        assert len(result) > 5

    def test_joke_es(self):
        result = plugin._joke("es")
        assert isinstance(result, str)
        assert len(result) > 10

    def test_joke_en(self):
        result = plugin._joke("en")
        assert isinstance(result, str)
        assert len(result) > 10

    def test_status_es(self):
        result = plugin._status("es")
        assert isinstance(result, str)
        assert len(result) > 5

    def test_insult_es(self):
        result = plugin._insult("es")
        assert isinstance(result, str)
        assert len(result) > 5

    def test_compliment_es(self):
        result = plugin._compliment("es")
        assert isinstance(result, str)
        assert len(result) > 5


class TestHandle:
    def test_greeting(self, bus):
        plugin.handle("greeting", "", bus)
        bus.emit.assert_called_once()
        event, msg = bus.emit.call_args[0]
        assert event == "speak"
        assert isinstance(msg, str)
        assert len(msg) > 0

    def test_joke(self, bus):
        plugin.handle("joke", "", bus)
        bus.emit.assert_called_once()
        event, msg = bus.emit.call_args[0]
        assert event == "speak"
        assert isinstance(msg, str)
        assert len(msg) > 0

    def test_how_are_you(self, bus):
        plugin.handle("how_are_you", "", bus)
        bus.emit.assert_called_once()
        event, msg = bus.emit.call_args[0]
        assert event == "speak"
        assert isinstance(msg, str)
        assert len(msg) > 0

    def test_who_are_you(self, bus):
        plugin.handle("who_are_you", "", bus)
        bus.emit.assert_called_once()
        event, msg = bus.emit.call_args[0]
        assert event == "speak"
        assert "j.a.r.v.i.s." in msg.lower()

    def test_thanks(self, bus):
        plugin.handle("thanks", "", bus)
        bus.emit.assert_called_once()
        event, msg = bus.emit.call_args[0]
        assert event == "speak"
        assert isinstance(msg, str)
        assert len(msg) > 0

    def test_compliment(self, bus):
        plugin.handle("compliment", "", bus)
        bus.emit.assert_called_once()
        event, msg = bus.emit.call_args[0]
        assert event == "speak"

    def test_insult(self, bus):
        plugin.handle("insult", "", bus)
        bus.emit.assert_called_once()
        event, msg = bus.emit.call_args[0]
        assert event == "speak"

    def test_status(self, bus):
        plugin.handle("status", "", bus)
        bus.emit.assert_called_once()
        event, msg = bus.emit.call_args[0]
        assert event == "speak"
        assert isinstance(msg, str)
        assert len(msg) > 0
