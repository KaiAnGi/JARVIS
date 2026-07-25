"""Tests for plugins/gmail/plugin.py"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

pytest.importorskip("googleapiclient", reason="google-api-python-client not installed")

from core.language import set_lang
from plugins.gmail import plugin


class TestParseTime:
    def test_24h(self):
        result = plugin._parse_time("14:30")
        assert result is not None
        assert result.hour == 14
        assert result.minute == 30

    def test_in_minutes(self):
        result = plugin._parse_time("in 5 minutes")
        assert result is not None
        assert result > datetime.now()

    def test_in_hours(self):
        result = plugin._parse_time("in 2 hours")
        assert result is not None
        assert result > datetime.now()

    def test_invalid(self):
        assert plugin._parse_time("not a time") is None

    def test_am_pm(self):
        result = plugin._parse_time("2:30 pm")
        assert result is not None
        assert result.hour == 14
        assert result.minute == 30

    def test_12h_no_am_pm(self):
        result = plugin._parse_time("9:15")
        assert result is not None
        assert result.hour == 9
        assert result.minute == 15

    def test_in_1_minute(self):
        result = plugin._parse_time("in 1 minute")
        assert result is not None
        assert result > datetime.now()


class TestConfirmationFlow:
    def setup_method(self):
        plugin._pending_confirm = None

    @patch("plugins.gmail.plugin._get_service")
    def test_delete_asks_confirmation(self, mock_get_service, bus):
        set_lang("es")
        mock_service = MagicMock()
        mock_service.users().messages().list().execute.return_value = {"messages": [{"id": "msg1"}]}
        mock_service.users().messages().get().execute.return_value = {
            "payload": {"headers": [{"name": "Subject", "value": "Test Subject"}]}
        }
        mock_get_service.return_value = mock_service

        plugin.handle("delete_email", "delete email", bus)
        bus.emit.assert_called()
        assert plugin._pending_confirm is not None
        assert plugin._pending_confirm["type"] == "delete"

    @patch("plugins.gmail.plugin._get_service")
    def test_delete_confirm_yes(self, mock_get_service, bus):
        set_lang("es")
        mock_service = MagicMock()
        mock_service.users().messages().list().execute.return_value = {"messages": [{"id": "msg1"}]}
        mock_service.users().messages().get().execute.return_value = {
            "payload": {"headers": [{"name": "Subject", "value": "Test"}]}
        }
        mock_get_service.return_value = mock_service

        plugin.handle("delete_email", "delete email", bus)
        plugin.handle("yes", "yes", bus)
        mock_service.users().messages().delete().execute.assert_called_once()
        assert plugin._pending_confirm is None

    @patch("plugins.gmail.plugin._get_service")
    def test_delete_confirm_no(self, mock_get_service, bus):
        set_lang("es")
        mock_service = MagicMock()
        mock_service.users().messages().list().execute.return_value = {"messages": [{"id": "msg1"}]}
        mock_service.users().messages().get().execute.return_value = {
            "payload": {"headers": [{"name": "Subject", "value": "Test"}]}
        }
        mock_get_service.return_value = mock_service

        plugin.handle("delete_email", "delete email", bus)
        bus.reset_mock()
        plugin.handle("no", "no", bus)
        mock_service.users().messages().delete.assert_not_called()
        assert plugin._pending_confirm is None
        # Verify cancel message was sent
        bus.emit.assert_called_once()
        event, msg = bus.emit.call_args[0]
        assert event == "speak"
        assert isinstance(msg, str)
        assert len(msg) > 0

    @patch("plugins.gmail.plugin._get_service")
    def test_send_asks_confirmation(self, mock_get_service, bus):
        set_lang("es")
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        plugin.handle("send_email", "send email to test@example.com subject Hello body World", bus)
        bus.emit.assert_called()
        assert plugin._pending_confirm is not None
        assert plugin._pending_confirm["type"] == "send"

    @patch("plugins.gmail.plugin._get_service")
    def test_send_no_recipient(self, mock_get_service, bus):
        set_lang("es")
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        plugin.handle("send_email", "send email", bus)
        bus.emit.assert_called_once()
        event, msg = bus.emit.call_args[0]
        assert event == "speak"
        assert isinstance(msg, str)
        assert len(msg) > 0

    @patch("plugins.gmail.plugin._get_service")
    def test_send_confirm_yes(self, mock_get_service, bus):
        set_lang("es")
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        plugin.handle("send_email", "send email to test@example.com subject Hello body World", bus)
        bus.reset_mock()
        plugin.handle("yes", "yes", bus)
        mock_service.users().messages().send.assert_called_once()
        assert plugin._pending_confirm is None
        bus.emit.assert_called_once()
        event, msg = bus.emit.call_args[0]
        assert event == "speak"
        assert isinstance(msg, str)
        assert len(msg) > 0

    @patch("plugins.gmail.plugin._get_service")
    def test_count_email(self, mock_get_service, bus):
        set_lang("es")
        mock_service = MagicMock()
        mock_service.users().messages().list().execute.return_value = {"messages": [{"id": "1"}, {"id": "2"}]}
        mock_get_service.return_value = mock_service

        plugin.handle("count_email", "how many emails", bus)
        event, msg = bus.emit.call_args[0]
        assert event == "speak"
        assert "2" in str(msg)

    @patch("plugins.gmail.plugin._get_service")
    def test_no_email(self, mock_get_service, bus):
        set_lang("es")
        mock_service = MagicMock()
        mock_service.users().messages().list().execute.return_value = {}
        mock_get_service.return_value = mock_service

        plugin.handle("count_email", "how many emails", bus)
        event, msg = bus.emit.call_args[0]
        assert event == "speak"
        assert "0" in str(msg)

    @patch("plugins.gmail.plugin._get_service")
    def test_delete_no_messages(self, mock_get_service, bus):
        set_lang("es")
        mock_service = MagicMock()
        mock_service.users().messages().list().execute.return_value = {}
        mock_get_service.return_value = mock_service

        plugin.handle("delete_email", "delete email", bus)
        bus.emit.assert_called_once()
        event, msg = bus.emit.call_args[0]
        assert event == "speak"
        assert isinstance(msg, str)
        assert len(msg) > 0

    @patch("plugins.gmail.plugin._get_service")
    def test_send_no_subject(self, mock_get_service, bus):
        set_lang("es")
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        plugin.handle("send_email", "send email to test@example.com", bus)
        bus.emit.assert_called_once()
        event, _msg = bus.emit.call_args[0]
        assert event == "speak"
