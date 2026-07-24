"""Spotify control plugin — play, pause, next, previous, volume."""

import json
import os
import threading
import urllib.request
import base64
from core.language import resp

CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET", "")
REDIRECT_URI = os.environ.get("SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback")
TOKEN_PATH = os.environ.get("SPOTIFY_TOKEN_PATH", "")
SCOPE = "user-modify-playback-state user-read-playback-state user-read-currently-playing"

_token_cache = {"access_token": "", "refresh_token": ""}
_token_lock = threading.Lock()


def init(bus):
    if not CLIENT_ID or not CLIENT_SECRET:
        print("[SPOTIFY] No SPOTIFY_CLIENT_ID/SECRET set — plugin disabled")
        return
    _load_token()


def handle(action: str, text: str, bus):
    if not CLIENT_ID or not CLIENT_SECRET:
        bus.emit("speak", resp("spotify_not_configured"))
        return

    token = _get_token()
    if not token:
        bus.emit("speak", resp("spotify_not_configured"))
        return

    endpoints = {
        "spotify_pause":    ("PUT",  "https://api.spotify.com/v1/player/pause"),
        "spotify_resume":   ("PUT",  "https://api.spotify.com/v1/player/play"),
        "spotify_next":     ("POST", "https://api.spotify.com/v1/player/next"),
        "spotify_previous": ("POST", "https://api.spotify.com/v1/player/previous"),
        "spotify_mute":     ("PUT",  "https://api.spotify.com/v1/player/volume?volume_percent=0"),
        "spotify_unmute":   ("PUT",  "https://api.spotify.com/v1/player/volume?volume_percent=50"),
    }

    if action in endpoints:
        method, url = endpoints[action]
        _api_call(method, url, token, bus, action)
    elif action == "spotify_volume":
        vol = _extract_volume(text)
        if vol is not None:
            url = f"https://api.spotify.com/v1/player/volume?volume_percent={vol}"
            _api_call("PUT", url, token, bus, action)
        else:
            bus.emit("speak", resp("spotify_volume_what"))
    elif action == "spotify_status":
        _get_current_track(token, bus)
    elif action == "spotify_play":
        query = _extract_query(text, ("play", "reproduce", "pon", "play on spotify", "reproduce en spotify"))
        if query:
            _search_and_play(query, token, bus)
        else:
            _api_call("PUT", "https://api.spotify.com/v1/player/play", token, bus, action)


def _api_call(method: str, url: str, token: str, bus, action: str):
    try:
        req = urllib.request.Request(url, method=method)
        req.add_header("Authorization", f"Bearer {token}")
        with urllib.request.urlopen(req, timeout=10) as resp_:
            status = resp_.status
        if status in (200, 204):
            msg_map = {
                "spotify_pause": "spotify_paused",
                "spotify_resume": "spotify_resumed",
                "spotify_next": "spotify_next",
                "spotify_previous": "spotify_previous",
                "spotify_mute": "spotify_muted",
                "spotify_unmute": "spotify_unmuted",
                "spotify_volume": "spotify_volume_set",
                "spotify_play": "spotify_playing",
            }
            bus.emit("speak", resp(msg_map.get(action, "spotify_ok")))
        elif status == 401:
            _refresh_token()
            with _token_lock:
                new_token = _token_cache.get("access_token", token)
            if new_token != token:
                _api_call(method, url, new_token, bus, action)
        else:
            bus.emit("speak", resp("spotify_error"))
    except urllib.error.HTTPError as e:
        if e.code == 401:
            _refresh_token()
            with _token_lock:
                new_token = _token_cache.get("access_token", token)
            if new_token != token:
                _api_call(method, url, new_token, bus, action)
        else:
            print(f"[SPOTIFY] API error: {e.code}")
            bus.emit("speak", resp("spotify_error"))
    except Exception as e:
        print(f"[SPOTIFY] Error: {e}")
        bus.emit("speak", resp("spotify_error"))


def _get_current_track(token: str, bus):
    try:
        req = urllib.request.Request("https://api.spotify.com/v1/player/currently-playing")
        req.add_header("Authorization", f"Bearer {token}")
        with urllib.request.urlopen(req, timeout=10) as resp_:
            data = json.loads(resp_.read().decode("utf-8"))
            if data and data.get("item"):
                name = data["item"]["name"]
                artists = ", ".join(a["name"] for a in data["item"]["artists"])
                bus.emit("speak", resp("spotify_now_playing", name=name, artists=artists))
            else:
                bus.emit("speak", resp("spotify_nothing"))
    except Exception:
        bus.emit("speak", resp("spotify_nothing"))


def _search_and_play(query: str, token: str, bus):
    try:
        from urllib.parse import quote_plus
        url = f"https://api.spotify.com/v1/search?q={quote_plus(query)}&type=track&limit=1"
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {token}")
        with urllib.request.urlopen(req, timeout=10) as resp_:
            data = json.loads(resp_.read().decode("utf-8"))
            tracks = data.get("tracks", {}).get("items", [])
            if tracks:
                uri = tracks[0]["uri"]
                play_req = urllib.request.Request(
                    "https://api.spotify.com/v1/player/play",
                    data=json.dumps({"uris": [uri]}).encode("utf-8"),
                    method="PUT",
                )
                play_req.add_header("Authorization", f"Bearer {token}")
                play_req.add_header("Content-Type", "application/json")
                urllib.request.urlopen(play_req, timeout=10)
                name = tracks[0]["name"]
                bus.emit("speak", resp("spotify_playing_track", name=name))
            else:
                bus.emit("speak", resp("spotify_not_found"))
    except Exception as e:
        print(f"[SPOTIFY] Search error: {e}")
        bus.emit("speak", resp("spotify_error"))


def _extract_volume(text: str) -> int | None:
    import re
    match = re.search(r'(\d+)', text)
    if match:
        vol = int(match.group(1))
        return max(0, min(100, vol))
    return None


def _extract_query(text: str, keywords: tuple) -> str:
    lower = text.lower()
    for kw in keywords:
        idx = lower.find(kw)
        if idx != -1:
            after = text[idx + len(kw):].strip()
            if after:
                return after
    return ""


def _get_token() -> str:
    return _token_cache.get("access_token", "")


def _load_token():
    global _token_cache
    if TOKEN_PATH and os.path.exists(TOKEN_PATH):
        try:
            data = json.loads(open(TOKEN_PATH).read())
            _token_cache = data
        except Exception:
            pass


def _save_token():
    if TOKEN_PATH:
        try:
            os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
            with open(TOKEN_PATH, "w") as f:
                json.dump(_token_cache, f)
        except Exception:
            pass


def _refresh_token():
    global _token_cache
    with _token_lock:
        refresh = _token_cache.get("refresh_token", "")
        if not refresh:
            return
        try:
            creds = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
            data = f"grant_type=refresh_token&refresh_token={refresh}".encode()
            req = urllib.request.Request(
                "https://accounts.spotify.com/api/token",
                data=data,
                headers={
                    "Authorization": f"Basic {creds}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            )
            with urllib.request.urlopen(req, timeout=10) as resp_:
                result = json.loads(resp_.read().decode("utf-8"))
                _token_cache["access_token"] = result["access_token"]
                if "refresh_token" in result:
                    _token_cache["refresh_token"] = result["refresh_token"]
                _save_token()
        except Exception as e:
            print(f"[SPOTIFY] Token refresh failed: {e}")
