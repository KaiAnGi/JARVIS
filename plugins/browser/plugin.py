"""browser plugin - Web searches and YouTube."""

import webbrowser
from urllib.parse import quote_plus


def init(bus):
    pass


def handle(action: str, text: str, bus):
    if action == "web_search":
        query = _extract_query(text, ("search for", "search", "google", "look up", "buscar", "busca"))
        if query:
            webbrowser.open(f"https://www.google.com/search?q={quote_plus(query)}")
            bus.emit("speak", f"Buscando {query} en Google")
        else:
            bus.emit("speak", "¿Qué debo buscar?")

    elif action == "youtube_search":
        query = _extract_query(text, ("youtube", "on youtube", "en youtube"))
        if query:
            webbrowser.open(f"https://www.youtube.com/results?search_query={quote_plus(query)}")
            bus.emit("speak", f"Buscando {query} en YouTube")
        else:
            bus.emit("speak", "¿Qué debo buscar en YouTube?")

    elif action == "youtube_play":
        query = _extract_query(text, ("play on youtube", "play", "youtube", "reproduce en youtube", "reproducir en youtube"))
        if query:
            webbrowser.open(f"https://www.youtube.com/results?search_query={quote_plus(query)}")
            bus.emit("speak", f"Reproduciendo {query} en YouTube")
        else:
            bus.emit("speak", "¿Qué debo reproducir?")

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
            bus.emit("speak", f"Abriendo {url}")
        else:
            bus.emit("speak", "¿Qué sitio web debo abrir?")


def _extract_query(text: str, prefixes: tuple) -> str:
    text = text.lower()
    for prefix in sorted(prefixes, key=len, reverse=True):
        if prefix in text:
            query = text.split(prefix, 1)[1].strip()
            if query:
                return query
    return ""
