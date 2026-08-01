"""Tests for plugins/system_control/plugin.py"""

from unittest.mock import patch

from core.language import set_lang
from plugins.system_control import plugin


class TestOpenBrowser:
    def test_launches_known_chrome_path(self, bus):
        set_lang("es")
        with patch("subprocess.Popen") as popen, patch(
            "os.path.isfile", side_effect=lambda p: p == plugin.BROWSER_CANDIDATES[-1]
        ):
            plugin._open_app("open browser", bus)
        popen.assert_called_once_with([plugin.BROWSER_CANDIDATES[-1]])
        bus.emit.assert_called_once_with("speak", plugin.resp("open_app", name="browser"))

    def test_falls_back_to_default_browser(self, bus):
        set_lang("es")
        with patch("os.path.isfile", return_value=False), patch("webbrowser.open") as wb:
            plugin._open_app("abre el navegador", bus)
        wb.assert_called_once_with("https://www.google.com")
        bus.emit.assert_called_once_with("speak", plugin.resp("open_app", name="navegador"))

    def test_browser_names_clean(self):
        for phrase in ("open browser", "abre el navegador", "open google chrome", "abre chrome"):
            name = plugin._clean_app_name(phrase)
            assert name in plugin.BROWSER_NAMES

    def test_chrome_alias_in_path_map(self):
        assert "chrome" in plugin.APPS_PATH
        assert "google chrome" in plugin.APPS_PATH
