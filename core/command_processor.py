"""Shared fallback for unmatched commands, used by both the CLI and the GUI."""

from core.language import resp


def process_unmatched(text: str, router, bus) -> bool:
    """Try to understand an unmatched command via Ollama. Returns True if handled."""
    from core.fuzzy_actions import execute_fuzzy_action
    from core.fuzzy_intent import is_ollama_ready, match_fuzzy

    try:
        if not is_ollama_ready():
            bus.emit("speak", resp("no_ollama"))
            return False
        result = match_fuzzy(text)
        if not result or result.get("action") == "unknown":
            bus.emit("speak", resp("no_match"))
            return False
        return execute_fuzzy_action(result, router, bus)
    except Exception:
        bus.emit("speak", resp("no_match"))
        return False
