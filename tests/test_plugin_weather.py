"""Tests for plugins/weather/plugin.py"""

import json
from unittest.mock import MagicMock, patch

from core.language import set_lang
from plugins.weather import plugin


class TestWeatherCodeToText:
    def test_clear_es(self):
        set_lang("es")
        assert plugin._weather_code_to_text(0) == "despejado"

    def test_clear_en(self):
        set_lang("en")
        assert plugin._weather_code_to_text(0) == "clear"

    def test_rain_es(self):
        set_lang("es")
        assert plugin._weather_code_to_text(63) == "lluvia"

    def test_rain_en(self):
        set_lang("en")
        assert plugin._weather_code_to_text(63) == "rain"

    def test_unknown_code_es(self):
        set_lang("es")
        result = plugin._weather_code_to_text(999)
        assert "999" in result

    def test_unknown_code_en(self):
        set_lang("en")
        result = plugin._weather_code_to_text(999)
        assert "999" in result

    def test_all_codes_have_translations(self):
        codes = [0, 1, 2, 3, 45, 48, 51, 53, 55, 61, 63, 65, 71, 73, 75, 80, 81, 82, 95, 96, 99]
        set_lang("es")
        for code in codes:
            result = plugin._weather_code_to_text(code)
            assert isinstance(result, str)
            assert len(result) > 0
        set_lang("en")
        for code in codes:
            result = plugin._weather_code_to_text(code)
            assert isinstance(result, str)
            assert len(result) > 0


class TestHandle:
    def test_get_weather_city_no_city(self, bus):
        plugin.handle("get_weather_city", "weather in", bus)
        bus.emit.assert_called_once()
        event, msg = bus.emit.call_args[0]
        assert event == "speak"
        assert isinstance(msg, str)
        assert len(msg) > 0

    @patch("plugins.weather.plugin.urllib.request.urlopen")
    def test_get_weather_city_found(self, mock_urlopen, bus):
        geo_resp = MagicMock()
        geo_resp.read.return_value = json.dumps(
            {"results": [{"latitude": 40.4, "longitude": -3.7, "name": "Madrid"}]}
        ).encode()
        geo_resp.__enter__ = lambda s: s
        geo_resp.__exit__ = MagicMock(return_value=False)

        wx_resp = MagicMock()
        wx_resp.read.return_value = json.dumps(
            {
                "current": {
                    "temperature_2m": 22,
                    "apparent_temperature": 20,
                    "relative_humidity_2m": 45,
                    "weather_code": 0,
                    "wind_speed_10m": 3.6,
                }
            }
        ).encode()
        wx_resp.__enter__ = lambda s: s
        wx_resp.__exit__ = MagicMock(return_value=False)

        mock_urlopen.side_effect = [geo_resp, wx_resp]

        plugin.handle("get_weather_city", "weather in Madrid", bus)
        bus.emit.assert_called_once()
        event, msg = bus.emit.call_args[0]
        assert event == "speak"
        assert "Madrid" in msg
        assert "22" in str(msg) or "grados" in msg.lower() or "degrees" in msg.lower()

    @patch("plugins.weather.plugin.urllib.request.urlopen")
    def test_get_weather_city_not_found(self, mock_urlopen, bus):
        geo_resp = MagicMock()
        geo_resp.read.return_value = json.dumps({"results": []}).encode()
        geo_resp.__enter__ = lambda s: s
        geo_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = geo_resp

        plugin.handle("get_weather_city", "weather in FakeCity", bus)
        bus.emit.assert_called_once()
        event, msg = bus.emit.call_args[0]
        assert event == "speak"
        assert "FakeCity" in msg

    @patch("plugins.weather.plugin.urllib.request.urlopen")
    def test_get_weather_network_error(self, mock_urlopen, bus):
        mock_urlopen.side_effect = Exception("network down")
        plugin.handle("get_weather_city", "weather in Madrid", bus)
        bus.emit.assert_called_once()
        event, _msg = bus.emit.call_args[0]
        assert event == "speak"

    def test_get_weather_default_city(self, bus):
        """get_weather (no city) should default to Madrid."""
        with patch.object(plugin, "_fetch_weather") as mock_fetch:
            plugin.handle("get_weather", "weather", bus)
            mock_fetch.assert_called_once_with("Madrid", bus)
