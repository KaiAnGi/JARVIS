"""browser plugin - Web searches and YouTube."""

import re
import threading
import time
import webbrowser
from urllib.parse import quote_plus

from core.language import resp
from core.text_utils import extract_after_keyword

_waiting_youtube = False
_waiting_youtube_ts = 0.0
_yt_lock = threading.Lock()
_YOUTUBE_TIMEOUT = 30.0


def reset_state():
    """Reset plugin state. Call on new session."""
    global _waiting_youtube, _waiting_youtube_ts
    with _yt_lock:
        _waiting_youtube = False
        _waiting_youtube_ts = 0.0


def is_waiting_youtube() -> bool:
    """Thread-safe check for pending YouTube follow-up."""
    with _yt_lock:
        if _waiting_youtube:
            if time.time() - _waiting_youtube_ts > _YOUTUBE_TIMEOUT:
                return False
            return True
        return False


def handle(action: str, text: str, bus):
    global _waiting_youtube, _waiting_youtube_ts

    with _yt_lock:
        waiting = _waiting_youtube

    if waiting:
        if is_waiting_youtube():
            _do_youtube_search(text, bus)
            return
        else:
            with _yt_lock:
                _waiting_youtube = False

    if action == "web_search":
        query = extract_after_keyword(text, ("search for", "search", "google", "look up", "buscar", "busca"))
        if query:
            webbrowser.open(f"https://www.google.com/search?q={quote_plus(query)}")
            bus.emit("speak", resp("search_google", query=query))
        else:
            bus.emit("speak", resp("what_search"))

    elif action == "youtube_search":
        query = extract_after_keyword(text, ("youtube", "you tube", "on youtube", "en youtube"))
        if query:
            _do_youtube_search(query, bus)
        else:
            with _yt_lock:
                _waiting_youtube = True
                _waiting_youtube_ts = time.time()
            bus.emit("speak", resp("what_youtube"))

    elif action == "youtube_play":
        query = extract_after_keyword(
            text, ("play on youtube", "play", "youtube", "reproduce en youtube", "reproducir en youtube")
        )
        if query:
            _do_youtube_search(query, bus)
        else:
            with _yt_lock:
                _waiting_youtube = True
                _waiting_youtube_ts = time.time()
            bus.emit("speak", resp("what_play"))

    elif action == "open_url":
        url = extract_after_keyword(text.lower(), ("open website", "abre sitio web", "abre página"))
        if url:
            if not url.startswith("http"):
                url = "https://" + url
            if not _is_valid_url(url):
                bus.emit("speak", resp("what_url"))
                return
            webbrowser.open(url)
            bus.emit("speak", resp("open_url", url=url))
        else:
            bus.emit("speak", resp("what_url"))


def _do_youtube_search(query: str, bus):
    global _waiting_youtube
    with _yt_lock:
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


def _is_valid_url(url: str) -> bool:
    """Basic URL validation — checks scheme and that there's a domain with TLD."""
    from urllib.parse import urlparse

    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        host = parsed.hostname or ""
        if not host or "." not in host:
            return False
        if len(host) < 3:
            return False
        return True
    except Exception:
        return False
