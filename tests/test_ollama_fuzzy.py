"""Tests for core/ollama_client.py and core/fuzzy_intent.py"""

from unittest.mock import patch, MagicMock
import json

from core import ollama_client, fuzzy_intent


class TestOllamaClient:
    @patch("core.ollama_client.urllib.request.urlopen")
    def test_is_available_true(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp
        assert ollama_client.is_available() is True

    @patch("core.ollama_client.urllib.request.urlopen", side_effect=Exception("refused"))
    def test_is_available_false(self, mock_urlopen):
        assert ollama_client.is_available() is False

    @patch("core.ollama_client.urllib.request.urlopen")
    def test_chat_returns_response(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"response": "hello world"}).encode()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = ollama_client.chat("test prompt")
        assert result == "hello world"

    @patch("core.ollama_client.urllib.request.urlopen")
    def test_chat_strips_think_tags(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(
            {"response": "<think>reasoning</think>actual answer"}
        ).encode()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = ollama_client.chat("test")
        assert "<think>" not in result
        assert "</think>" not in result
        assert "actual answer" in result

    @patch("core.ollama_client.urllib.request.urlopen", side_effect=Exception("error"))
    def test_chat_returns_empty_on_error(self, mock_urlopen):
        result = ollama_client.chat("test")
        assert result == ""


class TestFuzzyIntent:
    def setup_method(self):
        fuzzy_intent._available = None
        fuzzy_intent._last_check = 0.0

    @patch("core.fuzzy_intent.is_available", return_value=False)
    def test_not_ready(self, mock_avail):
        assert fuzzy_intent.is_ollama_ready() is False

    @patch("core.fuzzy_intent.is_available", return_value=True)
    def test_ready(self, mock_avail):
        assert fuzzy_intent.is_ollama_ready() is True

    @patch("core.fuzzy_intent.is_ollama_ready", return_value=False)
    def test_match_fuzzy_returns_none_when_not_ready(self, mock_ready):
        assert fuzzy_intent.match_fuzzy("hello") is None

    @patch("core.fuzzy_intent.chat", return_value='{"action": "open_app", "app": "notepad"}')
    @patch("core.fuzzy_intent.is_ollama_ready", return_value=True)
    def test_match_fuzzy_valid_json(self, mock_ready, mock_chat):
        result = fuzzy_intent.match_fuzzy("open notepad")
        assert result is not None
        assert result["action"] == "open_app"

    @patch("core.fuzzy_intent.chat", return_value="not json at all")
    @patch("core.fuzzy_intent.is_ollama_ready", return_value=True)
    def test_match_fuzzy_invalid_json(self, mock_ready, mock_chat):
        assert fuzzy_intent.match_fuzzy("something") is None

    @patch("core.fuzzy_intent.chat", return_value='{"action": "unknown"}')
    @patch("core.fuzzy_intent.is_ollama_ready", return_value=True)
    def test_match_fuzzy_unknown_action(self, mock_ready, mock_chat):
        result = fuzzy_intent.match_fuzzy("xyz")
        assert result is not None
        assert result["action"] == "unknown"

    @patch("core.fuzzy_intent.chat", return_value='```json\n{"action": "help"}\n```')
    @patch("core.fuzzy_intent.is_ollama_ready", return_value=True)
    def test_match_fuzzy_strips_markdown(self, mock_ready, mock_chat):
        result = fuzzy_intent.match_fuzzy("help")
        assert result is not None
        assert result["action"] == "help"

    @patch("core.fuzzy_intent.chat", return_value="")
    @patch("core.fuzzy_intent.is_ollama_ready", return_value=True)
    def test_match_fuzzy_empty_response(self, mock_ready, mock_chat):
        assert fuzzy_intent.match_fuzzy("test") is None
