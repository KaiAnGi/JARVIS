"""Tests for plugins/system_control/plugin.py"""

from unittest.mock import patch

from core.language import set_lang
from plugins.system_control import plugin


class TestOpenBrowser:
    def test_launches_default_browser_exe(self, bus):
        set_lang("es")
        with (
            patch.object(plugin, "_default_browser_exe", return_value=r"C:\browser\app.exe"),
            patch.object(plugin, "_focus_or_maximize_browser", return_value=False),
            patch("subprocess.Popen") as popen,
        ):
            plugin._open_app("open browser", bus)
        popen.assert_called_once_with([r"C:\browser\app.exe"])
        bus.emit.assert_called_once_with("speak", plugin.resp("open_app", name="browser"))

    def test_focuses_existing_browser_window(self, bus):
        set_lang("es")
        with (
            patch.object(plugin, "_default_browser_exe", return_value=r"C:\browser\app.exe"),
            patch.object(plugin, "_focus_or_maximize_browser", return_value=True),
            patch("subprocess.Popen") as popen,
        ):
            plugin._open_app("abre el navegador", bus)
        popen.assert_not_called()
        bus.emit.assert_called_once_with("speak", plugin.resp("browser_already_open"))

    def test_chrome_preferred_path_used(self, bus):
        set_lang("es")
        chrome = plugin.CHROME_CANDIDATES[0]
        with (
            patch("os.path.isfile", return_value=True),
            patch.object(plugin, "_focus_or_maximize_browser", return_value=False),
            patch("subprocess.Popen") as popen,
        ):
            plugin._open_app("open chrome", bus)
        popen.assert_called_once_with([chrome])

    def test_falls_back_to_default_browser(self, bus):
        set_lang("es")
        with (
            patch.object(plugin, "_default_browser_exe", return_value=None),
            patch("os.path.isfile", return_value=False),
            patch("webbrowser.open") as wb,
        ):
            plugin._open_app("abre el navegador", bus)
        wb.assert_called_once_with("https://www.google.com")
        bus.emit.assert_called_once_with("speak", plugin.resp("open_app", name="navegador"))

    def test_default_browser_names_clean(self):
        for phrase in ("open browser", "abre el navegador", "open default browser", "abre el navegador por defecto"):
            name = plugin._clean_app_name(phrase)
            assert name in plugin.BROWSER_NAMES

    def test_chrome_names_clean(self):
        for phrase in ("open chrome", "abre google chrome"):
            assert plugin._clean_app_name(phrase) in ("chrome", "google chrome")

    def test_parse_exe_from_command(self):
        assert (
            plugin._parse_exe_from_command(r'"C:\Pro gram Files\app.exe" --single %1') == r"C:\Pro gram Files\app.exe"
        )
        assert plugin._parse_exe_from_command(r"C:\path\app.exe %1") == r"C:\path\app.exe"
        assert plugin._parse_exe_from_command('""') is None
