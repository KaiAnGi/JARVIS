"""Tests for plugins/spotify_control/plugin.py"""

import json
from unittest.mock import MagicMock, patch

from plugins.spotify_control import plugin


class TestExtractVolume:
    def test_number(self):
        assert plugin._extract_volume("volume 50") == 50

    def test_clamped_high(self):
        assert plugin._extract_volume("volume 150") == 100

    def test_clamped_low(self):
        assert plugin._extract_volume("volume -10") == 10

    def test_no_number(self):
        assert plugin._extract_volume("volume") is None


class TestTokenManagement:
    def setup_method(self):
        plugin._token_cache = {"access_token": "", "refresh_token": ""}

    def test_load_token_no_path(self):
        plugin.TOKEN_PATH = ""
        plugin._load_token()  # Should not raise

    def test_get_token_empty(self):
        assert plugin._get_token() == ""

    @patch("builtins.open", create=True)
    def test_load_token_valid(self, mock_open):
        original_path = plugin.TOKEN_PATH
        plugin.TOKEN_PATH = "fake_token.json"
        mock_open.return_value.__enter__ = lambda s: s
        mock_open.return_value.__exit__ = MagicMock(return_value=False)
        mock_open.return_value.read.return_value = json.dumps(
            {"access_token": "test_token", "refresh_token": "test_refresh"}
        )
        with patch("plugins.spotify_control.plugin.os.path.exists", return_value=True):
            plugin._load_token()
        plugin.TOKEN_PATH = original_path
        assert plugin._token_cache["access_token"] == "test_token"


class TestHandle:
    def setup_method(self):
        plugin._token_cache = {"access_token": "", "refresh_token": ""}

    def test_no_credentials(self, bus):
        plugin.CLIENT_ID = ""
        plugin.CLIENT_SECRET = ""
        plugin.handle("spotify_pause", "", bus)
        bus.emit.assert_called_once()

    def test_no_token(self, bus):
        plugin.CLIENT_ID = "test_id"
        plugin.CLIENT_SECRET = "test_secret"
        plugin._token_cache = {"access_token": "", "refresh_token": ""}
        plugin.handle("spotify_pause", "", bus)
        bus.emit.assert_called_once()

    @patch("plugins.spotify_control.plugin.urllib.request.urlopen")
    def test_pause_success(self, mock_urlopen, bus):
        plugin.CLIENT_ID = "test_id"
        plugin.CLIENT_SECRET = "test_secret"
        plugin._token_cache = {"access_token": "valid_token", "refresh_token": "r"}

        mock_resp = MagicMock()
        mock_resp.status = 204
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        plugin.handle("spotify_pause", "", bus)
        bus.emit.assert_called_once()

    def test_volume_no_number(self, bus):
        plugin.CLIENT_ID = "test_id"
        plugin.CLIENT_SECRET = "test_secret"
        plugin._token_cache = {"access_token": "valid_token", "refresh_token": "r"}
        plugin.handle("spotify_volume", "volume", bus)
        bus.emit.assert_called_once()


class TestApiCallRetry:
    def setup_method(self):
        plugin._token_cache = {"access_token": "old_token", "refresh_token": "r"}

    @patch("plugins.spotify_control.plugin._refresh_token")
    @patch("plugins.spotify_control.plugin.urllib.request.urlopen")
    def test_no_infinite_recursion(self, mock_urlopen, mock_refresh, bus):
        """Verify _api_call doesn't recurse forever on repeated 401s."""
        from urllib.error import HTTPError

        mock_urlopen.side_effect = HTTPError(url="", code=401, msg="Unauthorized", hdrs=None, fp=None)
        plugin._api_call("PUT", "https://api.test", "token", bus, "spotify_pause")
        # Should emit error, not RecursionError
        bus.emit.assert_called()
