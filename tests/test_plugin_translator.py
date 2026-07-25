"""Tests for plugins/translator/plugin.py"""

import json
from unittest.mock import patch, MagicMock

from core.language import set_lang
from plugins.translator import plugin


class TestParseTranslate:
    def test_english_to_spanish(self):
        result = plugin._parse_translate("translate hello to spanish")
        assert result is not None
        assert result["text"] == "hello"
        assert result["dest"] == "es"

    def test_spanish_to_english(self):
        result = plugin._parse_translate("traduce hola a inglés")
        assert result is not None
        assert result["text"] == "hola"
        assert result["dest"] == "en"

    def test_no_match(self):
        assert plugin._parse_translate("hello world") is None

    def test_french(self):
        result = plugin._parse_translate("translate bonjour to french")
        assert result is not None
        assert result["dest"] == "fr"

    def test_german(self):
        result = plugin._parse_translate("translate hallo to german")
        assert result is not None
        assert result["dest"] == "de"

    def test_with_al_marker(self):
        result = plugin._parse_translate("traduce hola al inglés")
        assert result is not None
        assert result["dest"] == "en"
        assert result["text"] == "hola"

    def test_no_text(self):
        assert plugin._parse_translate("translate to french") is None


class TestLangNameToCode:
    def test_english(self):
        assert plugin._lang_name_to_code("english") == "en"

    def test_spanish(self):
        assert plugin._lang_name_to_code("spanish") == "es"

    def test_spanish_es(self):
        assert plugin._lang_name_to_code("español") == "es"

    def test_french(self):
        assert plugin._lang_name_to_code("french") == "fr"

    def test_unknown(self):
        assert plugin._lang_name_to_code("klingon") == ""

    def test_code_input(self):
        assert plugin._lang_name_to_code("en") == "en"
        assert plugin._lang_name_to_code("es") == "es"

    def test_german(self):
        assert plugin._lang_name_to_code("german") == "de"

    def test_portuguese(self):
        assert plugin._lang_name_to_code("portuguese") == "pt"

    def test_italian(self):
        assert plugin._lang_name_to_code("italian") == "it"


class TestHandle:
    def test_translate_no_match(self, bus):
        set_lang("es")
        plugin.handle("translate", "hello world", bus)
        bus.emit.assert_called_once()
        event, msg = bus.emit.call_args[0]
        assert event == "speak"
        assert isinstance(msg, str)
        assert len(msg) > 0

    @patch("plugins.translator.plugin.urllib.request.urlopen")
    def test_translate_success(self, mock_urlopen, bus):
        set_lang("es")
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps([
            [["hola", None], [None, "en"]]
        ]).encode()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        plugin.handle("translate", "translate hello to spanish", bus)
        bus.emit.assert_called_once()
        event, msg = bus.emit.call_args[0]
        assert event == "speak"
        assert "hola" in msg.lower()

    @patch("plugins.translator.plugin.urllib.request.urlopen")
    def test_translate_network_error(self, mock_urlopen, bus):
        set_lang("es")
        mock_urlopen.side_effect = Exception("network error")

        plugin.handle("translate", "translate hello to spanish", bus)
        bus.emit.assert_called_once()
        event, msg = bus.emit.call_args[0]
        assert event == "speak"

    def test_translate_to_english_no_match(self, bus):
        set_lang("es")
        plugin.handle("translate_to_english", "hello", bus)
        bus.emit.assert_called_once()

    def test_translate_to_spanish_no_match(self, bus):
        set_lang("es")
        plugin.handle("translate_to_spanish", "hello", bus)
        bus.emit.assert_called_once()
