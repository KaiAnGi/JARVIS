"""Tests for plugins/clipboard/plugin.py"""

from unittest.mock import patch

import pytest

pytest.importorskip("pyperclip", reason="pyperclip not installed")

from core.language import set_lang
from plugins.clipboard import plugin


class TestHandle:
    @patch("plugins.clipboard.plugin.pyperclip.paste", return_value="hello world")
    def test_read_clipboard(self, mock_paste, bus):
        set_lang("es")
        plugin.handle("clipboard_read", "", bus)
        bus.emit.assert_called_once()
        event, msg = bus.emit.call_args[0]
        assert event == "speak"
        assert "hello world" in msg

    @patch("plugins.clipboard.plugin.pyperclip.paste", return_value="")
    def test_read_empty(self, mock_paste, bus):
        set_lang("es")
        plugin.handle("clipboard_read", "", bus)
        bus.emit.assert_called_once()
        event, msg = bus.emit.call_args[0]
        assert event == "speak"
        assert isinstance(msg, str)
        assert len(msg) > 0

    @patch("plugins.clipboard.plugin.pyperclip.paste", side_effect=Exception("access denied"))
    def test_read_error(self, mock_paste, bus):
        set_lang("es")
        plugin.handle("clipboard_read", "", bus)
        bus.emit.assert_called_once()
        event, _msg = bus.emit.call_args[0]
        assert event == "speak"

    @patch("plugins.clipboard.plugin.pyperclip.copy")
    def test_copy(self, mock_copy, bus):
        set_lang("es")
        plugin.handle("clipboard_copy", "copy hello world", bus)
        mock_copy.assert_called_once_with("hello world")
        bus.emit.assert_called_once()
        event, _msg = bus.emit.call_args[0]
        assert event == "speak"

    def test_copy_nothing(self, bus):
        set_lang("es")
        plugin.handle("clipboard_copy", "copy", bus)
        bus.emit.assert_called_once()
        event, msg = bus.emit.call_args[0]
        assert event == "speak"
        assert isinstance(msg, str)
        assert len(msg) > 0

    @patch("plugins.clipboard.plugin.pyperclip.copy", side_effect=Exception("error"))
    def test_copy_error(self, mock_copy, bus):
        set_lang("es")
        plugin.handle("clipboard_copy", "copy something", bus)
        bus.emit.assert_called_once()
        event, _msg = bus.emit.call_args[0]
        assert event == "speak"

    @patch("pyautogui.hotkey")
    @patch("plugins.clipboard.plugin.pyperclip.paste", return_value="text")
    def test_paste(self, mock_paste, mock_hotkey, bus):
        plugin.handle("clipboard_paste", "", bus)
        mock_hotkey.assert_called_once_with("ctrl", "v")

    @patch("plugins.clipboard.plugin.pyperclip.paste", return_value="")
    def test_paste_empty(self, mock_paste, bus):
        set_lang("es")
        plugin.handle("clipboard_paste", "", bus)
        bus.emit.assert_called_once()
        event, _msg = bus.emit.call_args[0]
        assert event == "speak"

    @patch("plugins.clipboard.plugin.pyperclip.paste", side_effect=Exception("error"))
    def test_paste_error(self, mock_paste, bus):
        set_lang("es")
        plugin.handle("clipboard_paste", "", bus)
        bus.emit.assert_called_once()
        event, _msg = bus.emit.call_args[0]
        assert event == "speak"

    @patch("plugins.clipboard.plugin.pyperclip.paste", return_value="a" * 300)
    def test_read_truncates_long_content(self, mock_paste, bus):
        set_lang("es")
        plugin.handle("clipboard_read", "", bus)
        bus.emit.assert_called_once()
        event, msg = bus.emit.call_args[0]
        assert event == "speak"
        # The plugin truncates to 200 chars
        assert "a" * 200 in msg

    @patch("plugins.clipboard.plugin.pyperclip.copy")
    def test_copy_spanish(self, mock_copy, bus):
        set_lang("es")
        plugin.handle("clipboard_copy", "copiar hola mundo", bus)
        mock_copy.assert_called_once_with("hola mundo")
        bus.emit.assert_called_once()
