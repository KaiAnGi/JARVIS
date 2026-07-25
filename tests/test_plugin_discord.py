"""Tests for plugins/discord_notify/plugin.py"""

import json
from unittest.mock import patch, MagicMock

from core.language import set_lang
from plugins.discord_notify import plugin


class TestHandle:
    def setup_method(self):
        plugin.WEBHOOK_URL = ""

    def test_no_webhook_es(self, bus):
        set_lang("es")
        plugin.handle("discord_send", "send to discord hello", bus)
        bus.emit.assert_called_once()
        event, msg = bus.emit.call_args[0]
        assert event == "speak"
        assert isinstance(msg, str)
        assert len(msg) > 0

    def test_no_webhook_en(self, bus):
        set_lang("en")
        plugin.handle("discord_send", "send to discord hello", bus)
        bus.emit.assert_called_once()
        event, msg = bus.emit.call_args[0]
        assert event == "speak"

    @patch("plugins.discord_notify.plugin.WEBHOOK_URL", "https://hooks.example.com/test")
    @patch("plugins.discord_notify.plugin.urllib.request.urlopen")
    def test_send_message_success(self, mock_urlopen, bus):
        set_lang("es")
        mock_resp = MagicMock()
        mock_resp.status = 204
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        plugin.handle("discord_send", "send to discord hello world", bus)
        bus.emit.assert_called_once()
        event, msg = bus.emit.call_args[0]
        assert event == "speak"
        # Verify the webhook was called with the correct payload
        call_args = mock_urlopen.call_args
        req = call_args[0][0]
        assert req.full_url == "https://hooks.example.com/test"
        payload = json.loads(req.data.decode())
        assert payload["content"] == "hello world"

    @patch("plugins.discord_notify.plugin.WEBHOOK_URL", "https://hooks.example.com/test")
    def test_send_no_message(self, bus):
        set_lang("es")
        plugin.handle("discord_send", "send to discord", bus)
        bus.emit.assert_called_once()
        event, msg = bus.emit.call_args[0]
        assert event == "speak"
        assert isinstance(msg, str)
        assert len(msg) > 0

    @patch("plugins.discord_notify.plugin.WEBHOOK_URL", "https://hooks.example.com/test")
    @patch("plugins.discord_notify.plugin.urllib.request.urlopen")
    def test_send_failure(self, mock_urlopen, bus):
        set_lang("es")
        mock_urlopen.side_effect = Exception("network error")
        plugin.handle("discord_send", "send to discord test", bus)
        bus.emit.assert_called_once()
        event, msg = bus.emit.call_args[0]
        assert event == "speak"

    @patch("plugins.discord_notify.plugin.WEBHOOK_URL", "https://hooks.example.com/test")
    def test_notify_no_message(self, bus):
        set_lang("es")
        plugin.handle("discord_notify", "notify discord", bus)
        bus.emit.assert_called_once()

    @patch("plugins.discord_notify.plugin.WEBHOOK_URL", "https://hooks.example.com/test")
    @patch("plugins.discord_notify.plugin.urllib.request.urlopen")
    def test_notify_sends_notification_prefix(self, mock_urlopen, bus):
        mock_resp = MagicMock()
        mock_resp.status = 204
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        plugin.handle("discord_notify", "notify discord server is down", bus)
        req = mock_urlopen.call_args[0][0]
        payload = json.loads(req.data.decode())
        assert "Notificación" in payload["content"]
        assert "server is down" in payload["content"]
