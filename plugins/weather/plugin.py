"""Weather plugin — Open-Meteo (free, no API key needed)."""

import json
import urllib.request
from urllib.parse import quote_plus
from core.language import resp

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def init(bus):
    print("[WEATHER] Using Open-Meteo (free, no API key)")


def handle(action: str, text: str, bus):
    if action == "get_weather":
        city = _extract_city(text, ("weather", "clima", "tiempo", "temperatura", "how's the weather", "qué tiempo hace"))
        if not city:
            city = "Madrid"
        _fetch_weather(city, bus)

    elif action == "get_weather_city":
        city = _extract_city(text, ("weather in", "clima en", "tiempo en", "temperatura en"))
        if city:
            _fetch_weather(city, bus)
        else:
            bus.emit("speak", resp("weather_what_city"))


def _fetch_weather(city: str, bus):
    try:
        geo_req = urllib.request.Request(f"{GEO_URL}?name={quote_plus(city)}&count=1&language=es")
        with urllib.request.urlopen(geo_req, timeout=10) as resp_:
            geo_data = json.loads(resp_.read().decode("utf-8"))
            results = geo_data.get("results", [])
            if not results:
                bus.emit("speak", resp("weather_city_not_found", city=city))
                return
            lat = results[0]["latitude"]
            lon = results[0]["longitude"]
            city_name = results[0].get("name", city)

        wx_req = urllib.request.Request(
            f"{WEATHER_URL}?latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m"
            f"&temperature_unit=celsius&wind_speed_unit=kmh&timezone=auto"
        )
        with urllib.request.urlopen(wx_req, timeout=10) as resp_:
            wx = json.loads(resp_.read().decode("utf-8"))["current"]

        temp = round(wx["temperature_2m"])
        feels = round(wx["apparent_temperature"])
        humidity = wx["relative_humidity_2m"]
        wind = round(wx["wind_speed_10m"] / 3.6, 1)
        desc = _weather_code_to_text(wx["weather_code"])

        bus.emit("speak", resp(
            "weather_report",
            city=city_name,
            temp=temp,
            feels=feels,
            desc=desc,
            humidity=humidity,
            wind=wind,
        ))
    except Exception as e:
        print(f"[WEATHER] Error: {e}")
        bus.emit("speak", resp("weather_error"))


def _weather_code_to_text(code: int) -> str:
    mapping = {
        0: "despejado", 1: "mayormente despejado", 2: "parcialmente nublado", 3: "nublado",
        45: "niebla", 48: "niebla con escarcha",
        51: "llovizna ligera", 53: "llovizna", 55: "llovizna intensa",
        61: "lluvia ligera", 63: "lluvia", 65: "lluvia intensa",
        71: "nieve ligera", 73: "nieve", 75: "nieve intensa",
        80: "chubascos ligeros", 81: "chubascos", 82: "chubascos intensos",
        95: "tormenta", 96: "tormenta con granizo", 99: "tormenta fuerte con granizo",
    }
    return mapping.get(code, f"código {code}")


def _extract_city(text: str, keywords: tuple) -> str:
    lower = text.lower()
    for kw in keywords:
        idx = lower.find(kw)
        if idx != -1:
            after = text[idx + len(kw):].strip()
            if after:
                return after.strip("?.,!")
    return ""
