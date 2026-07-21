"""Language manager — single source of truth for locale, patterns, and UI strings."""

from pathlib import Path
import json

_current = "es"

MODELS = {
    "es": "vosk-model-small-es-0.42",
    "en": "vosk-model-small-en-us-0.15",
}

VOICES = {
    "es": "Spanish",
    "en": "English",
}

UI = {
    "es": {
        "window_title": "J.A.R.V.I.S.",
        "header": "J.A.R.V.I.S.",
        "subtitle": "Just A Rather Very Intelligent System",
        "placeholder": "Escribe un comando o di 'Hey Jarvis'...",
        "send": "ENVIAR",
        "activate": "ACTIVAR",
        "clear": "LIMPIAR",
        "session_active": "Sesión activa — habla tus comandos",
        "session_ended": "Sesión terminada — di 'Hey Jarvis' para reactivar",
        "listening": "Escuchando...",
        "yes": "¿Sí?",
        "goodbye": "Adiós",
        "lang_btn": "EN",
    },
    "en": {
        "window_title": "J.A.R.V.I.S.",
        "header": "J.A.R.V.I.S.",
        "subtitle": "Just A Rather Very Intelligent System",
        "placeholder": "Type a command or say 'Hey Jarvis'...",
        "send": "SEND",
        "activate": "ACTIVATE",
        "clear": "CLEAR",
        "session_active": "Session active — speak your commands",
        "session_ended": "Session ended — say 'Hey Jarvis' to reactivate",
        "listening": "Listening...",
        "yes": "Yes?",
        "goodbye": "Goodbye",
        "lang_btn": "ES",
    },
}

RESPONSES = {
    "es": {
        "time": "Son las {time}",
        "date": "Hoy es {day} {date}",
        "calc_result": "El resultado es {result}",
        "calc_error": "No pude entender ese cálculo",
        "open_app": "Abriendo {name}",
        "open_fail": "No pude encontrar {name}",
        "what_open": "¿Qué debo abrir?",
        "minimized": "Ventana minimizada",
        "maximized": "Ventana maximizada",
        "restored": "Ventana restaurada",
        "closed": "Ventana cerrada",
        "no_window": "No hay ventana activa",
        "min_error": "No pude minimizar la ventana",
        "max_error": "No pude cambiar la ventana",
        "close_error": "No pude cerrar la ventana",
        "open_explorer": "Abriendo explorador de archivos",
        "search_google": "Buscando {query} en Google",
        "search_youtube": "Buscando {query} en YouTube",
        "play_youtube": "Reproduciendo {query} en YouTube",
        "what_search": "¿Qué debo buscar?",
        "what_youtube": "¿Qué debo buscar en YouTube?",
        "what_play": "¿Qué debo reproducir?",
        "open_url": "Abriendo {url}",
        "what_url": "¿Qué sitio web debo abrir?",
        "count_email": "Tienes {count} correos sin leer",
        "check_email": "Correos recientes: {emails}",
        "read_email": "De {from}. Asunto: {subject}",
        "no_email": "No hay correos recientes",
        "no_read": "No hay correos para leer",
        "send_email": "Enviar correos por voz aún no está disponible por seguridad",
        "gmail_auth": "Gmail no está autenticado. Verifica credentials.json en config/",
        "list_events": "Eventos próximos: {events}",
        "next_event": "Próximo evento: {event} a las {time}",
        "no_events": "No hay eventos próximos",
        "create_event": "Crear eventos por voz aún no está disponible",
        "cal_auth": "Calendar no está autenticado. Verifica credentials.json en config/",
    },
    "en": {
        "time": "It's {time}",
        "date": "Today is {day}, {date}",
        "calc_result": "The answer is {result}",
        "calc_error": "Sorry, I couldn't understand that calculation",
        "open_app": "Opening {name}",
        "open_fail": "I couldn't find {name}",
        "what_open": "What should I open?",
        "minimized": "Window minimized",
        "maximized": "Window maximized",
        "restored": "Window restored",
        "closed": "Window closed",
        "no_window": "No active window found",
        "min_error": "Couldn't minimize the window",
        "max_error": "Couldn't change the window",
        "close_error": "Couldn't close the window",
        "open_explorer": "Opening file explorer",
        "search_google": "Searching Google for {query}",
        "search_youtube": "Searching YouTube for {query}",
        "play_youtube": "Playing {query} on YouTube",
        "what_search": "What should I search for?",
        "what_youtube": "What should I search on YouTube?",
        "what_play": "What should I play?",
        "open_url": "Opening {url}",
        "what_url": "Which website should I open?",
        "count_email": "You have {count} unread emails",
        "check_email": "Recent emails: {emails}",
        "read_email": "From {from}. Subject: {subject}",
        "no_email": "No recent emails",
        "no_read": "No emails to read",
        "send_email": "Sending email via voice is not yet supported for security reasons",
        "gmail_auth": "Gmail not authenticated. Check credentials.json in config/",
        "list_events": "Upcoming events: {events}",
        "next_event": "Next event: {event} at {time}",
        "no_events": "No upcoming events",
        "create_event": "Creating events via voice is not yet supported",
        "cal_auth": "Calendar not authenticated. Check credentials.json in config/",
    },
}

# ── Intent patterns per plugin per language ──────────────────────────
# key = action, value = list of patterns
INTENT_PATTERNS = {
    "datetime_calc": {
        "get_time":    {"en": ["what time"],              "es": ["qué hora", "que hora"]},
        "get_date":    {"en": ["what date", "what day"],   "es": ["qué fecha", "qué día", "que fecha", "que día"]},
        "calculate":   {"en": ["calculate", "what is", "what's"],
                        "es": ["calcular", "cuánto es", "cuanto es"]},
    },
    "system_control": {
        "open_app":       {"en": ["open", "launch"],       "es": ["abre", "iniciar"]},
        "minimize_window":{"en": ["minimize"],              "es": ["minimizar"]},
        "maximize_window":{"en": ["maximize"],              "es": ["maximizar"]},
        "close_window":   {"en": ["close window"],          "es": ["cierra ventana"]},
        "open_explorer":  {"en": ["open explorer"],         "es": ["abre explorador"]},
    },
    "browser": {
        "web_search":    {"en": ["search", "google"],       "es": ["buscar", "busca"]},
        "youtube_search":{"en": ["youtube"],                 "es": ["youtube"]},
        "youtube_play":  {"en": ["play on youtube", "play"], "es": ["reproduce en youtube", "reproducir en youtube"]},
        "open_url":      {"en": ["open website"],            "es": ["abre sitio web", "abre página"]},
    },
    "git_control": {
        "git_status": {"en": ["git status"], "es": ["git status"]},
        "git_commit": {"en": ["git commit"], "es": ["git commit"]},
        "git_push":   {"en": ["git push"],   "es": ["git push"]},
        "git_pull":   {"en": ["git pull"],   "es": ["git pull"]},
        "git_log":    {"en": ["git log"],    "es": ["git log"]},
    },
    "vscode_control": {
        "open_project": {"en": ["open project"], "es": ["abre proyecto"]},
        "open_vscode":  {"en": ["open vscode"],  "es": ["abre vscode"]},
        "open_file":    {"en": ["open file"],     "es": ["abre archivo"]},
        "run_task":     {"en": ["run task"],      "es": ["ejecuta tarea"]},
    },
    "gmail": {
        "check_email": {"en": ["check email"],           "es": ["revisa correo", "revisar correo"]},
        "read_email":  {"en": ["read email"],            "es": ["lee correo", "leer correo"]},
        "send_email":  {"en": ["send email"],            "es": ["envía correo", "enviar correo"]},
        "count_email": {"en": ["how many emails"],       "es": ["cuántos correos", "cuantos correos"]},
    },
    "calendar": {
        "list_events": {"en": ["what's on my calendar", "my schedule"],
                        "es": ["qué hay en mi calendario", "mi agenda"]},
        "next_event":  {"en": ["what's next"],            "es": ["qué sigue", "que sigue", "próximo evento"]},
        "create_event":{"en": ["create event", "add to calendar"],
                        "es": ["crear evento", "agregar al calendario"]},
    },
}

WAKE_PHRASES = {
    "en": ["goodbye jarvis", "bye jarvis", "exit jarvis", "close jarvis"],
    "es": ["adiós jarvis", "adios jarvis", "hasta luego jarvis", "chao jarvis"],
}


def get_lang() -> str:
    return _current


def set_lang(lang: str):
    global _current
    _current = lang


def toggle_lang() -> str:
    global _current
    _current = "en" if _current == "es" else "es"
    return _current


def ui(key: str) -> str:
    return UI[_current][key]


def resp(key: str, **kwargs) -> str:
    template = RESPONSES[_current][key]
    return template.format(**kwargs) if kwargs else template


def patterns_for(plugin: str, action: str) -> list[str]:
    return INTENT_PATTERNS.get(plugin, {}).get(action, {}).get(_current, [])


def all_patterns() -> dict:
    """Return {plugin: {action: [patterns]}} for current language."""
    out = {}
    for plugin, actions in INTENT_PATTERNS.items():
        out[plugin] = {}
        for action, langs in actions.items():
            out[plugin][action] = langs.get(_current, [])
    return out


def is_goodbye(text: str) -> bool:
    lower = text.lower().strip()
    return any(p in lower for p in WAKE_PHRASES[_current])
