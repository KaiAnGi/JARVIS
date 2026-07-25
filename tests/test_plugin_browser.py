"""Tests for plugins/browser/plugin.py"""

from unittest.mock import patch, MagicMock

from plugins.browser import plugin


class TestIsValidUrl:
    def test_valid_https(self):
        assert plugin._is_valid_url("https://google.com") is True

    def test_valid_http(self):
        assert plugin._is_valid_url("http://example.org") is True

    def test_no_scheme(self):
        assert plugin._is_valid_url("google.com") is False

    def test_no_tld(self):
        assert plugin._is_valid_url("https://localhost") is False

    def test_empty_host(self):
        assert plugin._is_valid_url("https://") is False

    def test_ip_address(self):
        assert plugin._is_valid_url("https://192.168.1.1") is True

    def test_subdomain(self):
        assert plugin._is_valid_url("https://mail.google.com") is True

    def test_path(self):
        assert plugin._is_valid_url("https://example.com/path/to/page") is True

    def test_long_tld(self):
        assert plugin._is_valid_url("https://example.museum") is True


class TestResetState:
    def test_reset(self):
        plugin._waiting_youtube = True
        plugin._waiting_youtube_ts = 12345.0
        plugin.reset_state()
        assert plugin._waiting_youtube is False
        assert plugin._waiting_youtube_ts == 0.0


class TestHandle:
    @patch("plugins.browser.plugin.webbrowser.open")
    def test_web_search(self, mock_open, bus):
        plugin.handle("web_search", "search for python tutorials", bus)
        mock_open.assert_called_once()
        assert "python" in mock_open.call_args[0][0].lower()

    @patch("plugins.browser.plugin.webbrowser.open")
    def test_open_url_valid(self, mock_open, bus):
        plugin.handle("open_url", "open website https://google.com", bus)
        mock_open.assert_called_once_with("https://google.com")

    @patch("plugins.browser.plugin.webbrowser.open")
    def test_open_url_adds_scheme(self, mock_open, bus):
        plugin.handle("open_url", "open website google.com", bus)
        mock_open.assert_called_once_with("https://google.com")

    def test_open_url_invalid(self, bus):
        plugin.handle("open_url", "open website not a url", bus)
        bus.emit.assert_called()
        # Should emit "what_url" since the URL is invalid

    def test_web_search_no_query(self, bus):
        plugin.handle("web_search", "search", bus)
        bus.emit.assert_called()
        emitted = bus.emit.call_args[0]
        assert "what_search" in emitted[1] or "buscar" in emitted[1]

    def test_youtube_search(self, bus):
        with patch("plugins.browser.plugin.threading.Thread") as mock_thread:
            plugin.handle("youtube_search", "youtube metallica", bus)
            mock_thread.assert_called_once()
