"""browser plugin - Web searches and YouTube."""

import webbrowser
from urllib.parse import quote_plus


def init(bus):
    pass


def handle(action: str, text: str, bus):
    if action == "web_search":
        query = _extract_query(text, ("search for", "search", "google", "look up"))
        if query:
            webbrowser.open(f"https://www.google.com/search?q={quote_plus(query)}")
            bus.emit("speak", f"Searching Google for {query}")
        else:
            bus.emit("speak", "What should I search for?")

    elif action == "youtube_search":
        query = _extract_query(text, ("youtube", "on youtube"))
        if query:
            webbrowser.open(f"https://www.youtube.com/results?search_query={quote_plus(query)}")
            bus.emit("speak", f"Searching YouTube for {query}")
        else:
            bus.emit("speak", "What should I search on YouTube?")

    elif action == "youtube_play":
        query = _extract_query(text, ("play on youtube", "play", "youtube"))
        if query:
            webbrowser.open(f"https://www.youtube.com/results?search_query={quote_plus(query)}")
            bus.emit("speak", f"Playing {query} on YouTube")
        else:
            bus.emit("speak", "What should I play?")

    elif action == "open_url":
        url = text.lower().split("open website", 1)[1].strip()
        if url:
            if not url.startswith("http"):
                url = "https://" + url
            webbrowser.open(url)
            bus.emit("speak", f"Opening {url}")
        else:
            bus.emit("speak", "Which website should I open?")


def _extract_query(text: str, prefixes: tuple) -> str:
    text = text.lower()
    for prefix in sorted(prefixes, key=len, reverse=True):
        if prefix in text:
            query = text.split(prefix, 1)[1].strip()
            if query:
                return query
    return ""
