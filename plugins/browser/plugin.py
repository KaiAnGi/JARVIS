"""browser plugin - Web searches and YouTube."""

import webbrowser
from urllib.parse import quote_plus

from core.language import resp


def init(bus):
    pass


def handle(action: str, text: str, bus):
    if action == "web_search":
        query = _extract_query(text, ("search for", "search", "google", "look up", "buscar", "busca"))
        if query:
            webbrowser.open(f"https://www.google.com/search?q={quote_plus(query)}")
            bus.emit("speak", resp("search_google", query=query))
        else:
            bus.emit("speak", resp("what_search"))

    elif action == "youtube_search":
        query = _extract_query(text, ("youtube", "on youtube", "en youtube"))
        if query:
            webbrowser.open(f"https://www.youtube.com/results?search_query={quote_plus(query)}")
            bus.emit("speak", resp("search_youtube", query=query))
        else:
            bus.emit("speak", resp("what_youtube"))

    elif action == "youtube_play":
        query = _extract_query(text, ("play on youtube", "play", "youtube",
                                       "reproduce en youtube", "reproducir en youtube"))
        if query:
            webbrowser.open(f"https://www.youtube.com/results?search_query={quote_plus(query)}")
            bus.emit("speak", resp("play_youtube", query=query))
        else:
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


def _extract_query(text: str, prefixes: tuple) -> str:
    text = text.lower()
    for prefix in sorted(prefixes, key=len, reverse=True):
        if prefix in text:
            query = text.split(prefix, 1)[1].strip()
            if query:
                return query
    return ""
