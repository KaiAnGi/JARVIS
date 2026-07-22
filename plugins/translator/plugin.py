"""Translator plugin — translate text using Google Translate (free, no API key)."""

import json
import urllib.request
from urllib.parse import quote_plus
from core.language import resp

GOOGLE_TRANSLATE_URL = "https://translate.googleapis.com/translate_a/single"


def init(bus):
    print("[TRANSLATOR] Using Google Translate (free)")


def handle(action: str, text: str, bus):
    if action == "translate":
        parsed = _parse_translate(text)
        if parsed:
            _do_translate(parsed["text"], parsed["src"], parsed["dest"], bus)
        else:
            bus.emit("speak", resp("translate_what"))

    elif action == "translate_to_english":
        content = _extract_content(text, ("translate to english", "traduce al inglés", "traducir al inglés"))
        if content:
            _do_translate(content, "auto", "en", bus)
        else:
            bus.emit("speak", resp("translate_what"))

    elif action == "translate_to_spanish":
        content = _extract_content(text, ("translate to spanish", "traduce al español", "traducir al español"))
        if content:
            _do_translate(content, "auto", "es", bus)
        else:
            bus.emit("speak", resp("translate_what"))


def _do_translate(text: str, src: str, dest: str, bus):
    try:
        params = f"?client=gtx&sl={src}&tl={dest}&dt=t&q={quote_plus(text)}"
        url = f"{GOOGLE_TRANSLATE_URL}{params}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp_:
            data = json.loads(resp_.read().decode("utf-8"))
            translated = "".join(part[0] for part in data[0] if part[0])
            if translated:
                bus.emit("speak", resp("translate_result", text=translated))
            else:
                bus.emit("speak", resp("translate_error"))
    except Exception as e:
        print(f"[TRANSLATOR] Error: {e}")
        bus.emit("speak", resp("translate_error"))


def _parse_translate(text: str) -> dict | None:
    lower = text.lower()
    to_markers = [" to ", " a ", " al ", " a la "]
    for marker in to_markers:
        idx = lower.find(marker)
        if idx != -1:
            content = text[:idx].strip()
            for prefix in ("translate", "traduce", "traducir"):
                if content.lower().startswith(prefix):
                    content = content[len(prefix):].strip()
                    break
            target_lang = text[idx + len(marker):].strip()
            lang_code = _lang_name_to_code(target_lang)
            if content and lang_code:
                return {"text": content, "src": "auto", "dest": lang_code}
    return None


def _extract_content(text: str, keywords: tuple) -> str:
    lower = text.lower()
    for kw in keywords:
        idx = lower.find(kw)
        if idx != -1:
            after = text[idx + len(kw):].strip()
            if after:
                return after
    return ""


def _lang_name_to_code(name: str) -> str:
    mapping = {
        "english": "en", "inglés": "en", "ingles": "en", "en": "en",
        "spanish": "es", "español": "es", "espanol": "es", "es": "es",
        "french": "fr", "francés": "fr", "frances": "fr", "fr": "fr",
        "german": "de", "alemán": "de", "aleman": "de", "de": "de",
        "portuguese": "pt", "portugués": "pt", "pt": "pt",
        "italian": "it", "italiano": "it", "it": "it",
        "japanese": "ja", "japonés": "ja", "ja": "ja",
        "chinese": "zh", "chino": "zh", "zh": "zh",
        "russian": "ruso", "ru": "ru",
        "arabic": "ar", "árabe": "ar", "ar": "ar",
    }
    return mapping.get(name.lower(), "")
