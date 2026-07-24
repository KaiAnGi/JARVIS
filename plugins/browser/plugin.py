"""browser plugin - Web searches and YouTube."""

import re
import threading
import time
import webbrowser
from urllib.parse import quote_plus

from core.language import resp

_waiting_youtube = False
_waiting_youtube_ts = 0.0
_YOUTUBE_TIMEOUT = 30.0


def init(bus):
    pass


def reset_state():
    """Reset plugin state. Call on new session."""
    global _waiting_youtube, _waiting_youtube_ts
    _waiting_youtube = False
    _waiting_youtube_ts = 0.0


def handle(action: str, text: str, bus):
    global _waiting_youtube, _waiting_youtube_ts

    if _waiting_youtube:
        if time.time() - _waiting_youtube_ts > _YOUTUBE_TIMEOUT:
            _waiting_youtube = False
        else:
            _do_youtube_search(text, bus)
            return

    if action == "web_search":
        query = _extract_query(text, ("search for", "search", "google", "look up", "buscar", "busca"))
        if query:
            webbrowser.open(f"https://www.google.com/search?q={quote_plus(query)}")
            bus.emit("speak", resp("search_google", query=query))
        else:
            bus.emit("speak", resp("what_search"))

    elif action == "youtube_search":
        query = _extract_query(text, ("youtube", "you tube", "on youtube", "en youtube"))
        if query:
            _do_youtube_search(query, bus)
        else:
            _waiting_youtube = True
            _waiting_youtube_ts = time.time()
            bus.emit("speak", resp("what_youtube"))

    elif action == "youtube_play":
        query = _extract_query(text, ("play on youtube", "play", "youtube",
                                       "reproduce en youtube", "reproducir en youtube"))
        if query:
            _do_youtube_search(query, bus)
        else:
            _waiting_youtube = True
            _waiting_youtube_ts = time.time()
            bus.emit("speak", resp("what_play"))

    elif action == "open_url":
        url = text.lower()
        for prefix in ("open website", "abre sitio web", "abre página"):
            if prefix in url:
                url = url.split(prefix, 1)[1].strip()
                break
        if url:
            if not url.startswith("http"):
                url = "https://" + url
            webbrowser.open(url)
            bus.emit("speak", resp("open_url", url=url))
        else:
            bus.emit("speak", resp("what_url"))


def _do_youtube_search(query: str, bus):
    global _waiting_youtube
    _waiting_youtube = False
    threading.Thread(target=_open_first_video, args=(query,), daemon=True).start()
    bus.emit("speak", resp("play_youtube", query=query))


def _open_first_video(query: str):
    try:
        import urllib.request
        url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        html = urllib.request.urlopen(req, timeout=5).read().decode("utf-8", errors="ignore")
        match = re.search(r'"videoId":"([^"]+)"', html)
        if match:
            webbrowser.open(f"https://www.youtube.com/watch?v={match.group(1)}")
        else:
            webbrowser.open(url)
    except Exception:
        webbrowser.open(f"https://www.youtube.com/results?search_query={quote_plus(query)}")


def _extract_query(text: str, prefixes: tuple) -> str:
    text = text.lower()
    for prefix in sorted(prefixes, key=len, reverse=True):
        if prefix in text:
            query = text.split(prefix, 1)[1].strip()
            if query:
                return query
    return ""
