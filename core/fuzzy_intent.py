"""Fuzzy intent matching using Ollama for unmatched voice commands.

Requires Ollama running locally. If not available, returns None gracefully.
Set JARVIS_OLLAMA_MODEL env var to use a different model (default: qwen3:8b).
"""

import json

from core.ollama_client import chat, is_available, MODEL
from core.language import get_lang

_available = None


def is_ollama_ready() -> bool:
    """Check once if Ollama is available, cache the result."""
    global _available
    if _available is None:
        _available = is_available()
        if not _available:
            print("[FUZZY] Ollama not available — fuzzy intent disabled")
    return _available


SYSTEM_PROMPT = """You are J.A.R.V.I.S., a voice assistant. When a voice command doesn't match any known pattern, you must figure out what the user wants and return a JSON object with the action to take.

Available actions and their parameters:

OPEN APP:
  {"action": "open_app", "app": "<app_name>"}
  Apps: notepad, calculator, paint, explorer, chrome, edge, steam, discord, epic games, ea, rockstar, winrar, minecraft, unity, intellij, obs, office, word, excel, powerpoint, vs code, vscode, wattpad, whatsapp, spotify

WEB SEARCH:
  {"action": "web_search", "query": "<search_query>"}

YOUTUBE:
  {"action": "youtube_search", "query": "<search_query>"}

EMAIL:
  {"action": "check_email"}
  {"action": "read_email"}
  {"action": "count_email"}

CALENDAR:
  {"action": "list_events"}
  {"action": "next_event"}

TIME/DATE:
  {"action": "get_time"}
  {"action": "get_date"}

CALCULATE:
  {"action": "calculate", "expression": "<math_expression>"}

WINDOW:
  {"action": "minimize_window"}
  {"action": "maximize_window"}
  {"action": "close_window"}

ALARM:
  {"action": "set_alarm", "time": "<HH:MM>", "repetition": "none|daily|weekdays|weekends", "message": "<optional_message>"}

TIMER:
  {"action": "start_timer", "duration": "<number>", "unit": "minutes|hours|seconds"}

STOPWATCH:
  {"action": "start_stopwatch"}
  {"action": "stop_stopwatch"}
  {"action": "read_stopwatch"}
  {"action": "reset_stopwatch"}

GIT:
  {"action": "git_status"}
  {"action": "git_commit", "message": "<commit_message>"}
  {"action": "git_push"}
  {"action": "git_pull"}

TAB:
  {"action": "close_tab"}
  {"action": "new_tab"}
  {"action": "duplicate_tab"}

Help:
  {"action": "help"}

If you truly cannot understand what the user wants, return:
  {"action": "unknown"}

Reply ONLY with valid JSON. No explanation, no markdown, no code blocks."""

LANG_HINTS = {
    "es": "El usuario habla español. Responde solo con el JSON.",
    "en": "The user speaks English. Reply only with the JSON.",
}


def match_fuzzy(text: str) -> dict | None:
    """Try to understand an unmatched voice command using Ollama.

    Returns None if Ollama is not available or returns invalid JSON.
    """
    if not is_ollama_ready():
        return None

    lang = get_lang()
    hint = LANG_HINTS.get(lang, "")
    prompt = f"{hint}\n\nUser said: \"{text}\""

    response = chat(prompt, system=SYSTEM_PROMPT)
    if not response:
        return None

    response = response.strip()
    if response.startswith("```"):
        response = response.split("\n", 1)[-1]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()

    try:
        parsed = json.loads(response)
        if isinstance(parsed, dict) and "action" in parsed:
            return parsed
    except json.JSONDecodeError:
        pass

    return None
