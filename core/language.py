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
        "open_fail": "No encontré {name}. ¿Está instalado?",
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
        "what_youtube": "¿Qué quieres ver en YouTube?",
        "what_play": "¿Qué debo reproducir?",
        "open_url": "Abriendo {url}",
        "what_url": "¿Qué sitio web debo abrir?",
        "count_email": "Tienes {count} correos sin leer",
        "check_email": "Correos recientes: {emails}",
        "read_email": "De {from}. Asunto: {subject}",
        "no_email": "No hay correos recientes",
        "no_read": "No hay correos para leer",
        "send_email": "Enviar correos por voz aún no está disponible por seguridad",
        "email_deleted": "Correo '{subject}' eliminado",
        "email_sent": "Correo enviado a {to}",
        "email_who": "¿A quién debo enviar el correo?",
        "email_what_subject": "¿Cuál es el asunto?",
        "email_when": "¿A qué hora debo enviarlo? Di 'a las' seguido de la hora.",
        "email_time_error": "No pude entender la hora. Di 'a las' seguido de la hora.",
        "email_scheduled": "Correo programado para {to} a las {time}",
        "email_scheduled_sent": "Correo enviado a {to} a las {time}",
        "gmail_auth": "Gmail no está autenticado. Verifica credentials.json en config/",
        "alarm_set": "Alarma puesta a las {time} {repetition}",
        "alarm_when": "¿A qué hora debo poner la alarma?",
        "alarm_time_error": "No pude entender la hora. Di 'a las' seguido de la hora.",
        "alarm_cancelled": "Alarma de las {time} cancelada",
        "alarm_cancel_all": "Todas las alarmas canceladas ({count})",
        "alarm_none": "No hay alarmas activas",
        "alarm_list": "Alarmas: {alarms}",
        "alarm_default_msg": "¡Alarma! ¡Es hora de despertar!",
        "timer_started": "Temporizador iniciado: {time}",
        "timer_how_long": "¿Cuánto tiempo? Di 'minutos' o 'horas'.",
        "timer_done": "¡Tiempo! El temporizador ha terminado.",
        "timer_stopped": "Temporizador cancelado",
        "stopwatch_started": "Cronómetro iniciado",
        "stopwatch_stopped": "Cronómetro parado: {time}",
        "stopwatch_reset": "Cronómetro reiniciado",
        "stopwatch_elapsed": "Tiempo transcurrido: {time}",
        "stopwatch_paused": "Cronómetro en pausa: {time}",
        "stopwatch_running": "El cronómetro ya está en marcha",
        "stopwatch_not_running": "El cronómetro no está en marcha",
        "stopwatch_not_started": "El cronómetro no se ha iniciado",
        "list_events": "Tienes: {events}",
        "next_event": "Siguiente evento: {event} {time}",
        "no_events": "No hay eventos próximos",
        "create_event": "Crear eventos por voz aún no está disponible",
        "cal_auth": "Calendar no está autenticado. Verifica credentials.json en config/",
        "tab_closed": "Pestaña cerrada",
        "tab_new": "Nueva pestaña abierta",
        "tab_duplicated": "Pestaña duplicada",
        "tab_switched": "Abriendo selector de pestañas",
        "tab_reopened": "Pestaña restaurada",
        "address_focused": "Barra de direcciones enfocada",
        "no_browser": "No hay navegador activo. ¿Abro uno?",
        "tab_error": "No pude realizar esa acción",
        "language_changed": "Idioma cambiado a {lang}",
        "language_set_es": "Idioma cambiado a Español",
        "language_set_en": "Idioma cambiado a Inglés",
        "help_summary": "Puedo ayudarte con lo siguiente: {summary}",
        "help_list": "Puedo ayudarte con: {categories}. ¿Con cuál necesitas ayuda?",
        "help_not_found": "No encontré esa categoría. Di 'ayuda' para ver las opciones.",
        "no_match": "No estoy seguro de entender. ¿Puedes repetirlo o decir 'ayuda'?",
    },
    "en": {
        "time": "It's {time}",
        "date": "Today is {day}, {date}",
        "calc_result": "The answer is {result}",
        "calc_error": "Sorry, I couldn't understand that calculation",
        "open_app": "Opening {name}",
        "open_fail": "I couldn't find {name}. Is it installed?",
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
        "what_youtube": "What do you want to watch on YouTube?",
        "what_play": "What should I play?",
        "open_url": "Opening {url}",
        "what_url": "Which website should I open?",
        "count_email": "You have {count} unread emails",
        "check_email": "Recent emails: {emails}",
        "read_email": "From {from}. Subject: {subject}",
        "no_email": "No recent emails",
        "no_read": "No emails to read",
        "send_email": "Sending email via voice is not yet supported for security reasons",
        "email_deleted": "Email '{subject}' deleted",
        "email_sent": "Email sent to {to}",
        "email_who": "Who should I send the email to?",
        "email_what_subject": "What's the subject?",
        "email_when": "When should I send it? Say 'at' followed by the time.",
        "email_time_error": "I couldn't understand the time. Say 'at' followed by the time.",
        "email_scheduled": "Email scheduled for {to} at {time}",
        "email_scheduled_sent": "Email sent to {to} at {time}",
        "gmail_auth": "Gmail not authenticated. Check credentials.json in config/",
        "alarm_set": "Alarm set for {time} {repetition}",
        "alarm_when": "What time should I set the alarm?",
        "alarm_time_error": "I couldn't understand the time. Say 'at' followed by the time.",
        "alarm_cancelled": "Alarm at {time} cancelled",
        "alarm_cancel_all": "All alarms cancelled ({count})",
        "alarm_none": "No active alarms",
        "alarm_list": "Alarms: {alarms}",
        "alarm_default_msg": "Alarm! Time to wake up!",
        "timer_started": "Timer started: {time}",
        "timer_how_long": "How long? Say 'minutes' or 'hours'.",
        "timer_done": "Time's up! The timer has finished.",
        "timer_stopped": "Timer cancelled",
        "stopwatch_started": "Stopwatch started",
        "stopwatch_stopped": "Stopwatch stopped: {time}",
        "stopwatch_reset": "Stopwatch reset",
        "stopwatch_elapsed": "Elapsed time: {time}",
        "stopwatch_paused": "Stopwatch paused: {time}",
        "stopwatch_running": "Stopwatch is already running",
        "stopwatch_not_running": "Stopwatch is not running",
        "stopwatch_not_started": "Stopwatch has not been started",
        "list_events": "You have: {events}",
        "next_event": "Next event: {event} {time}",
        "no_events": "No upcoming events",
        "create_event": "Creating events via voice is not yet supported",
        "cal_auth": "Calendar not authenticated. Check credentials.json in config/",
        "tab_closed": "Tab closed",
        "tab_new": "New tab opened",
        "tab_duplicated": "Tab duplicated",
        "tab_switched": "Opening tab picker",
        "tab_reopened": "Tab restored",
        "address_focused": "Address bar focused",
        "no_browser": "No active browser found. Should I open one?",
        "tab_error": "Couldn't perform that action",
        "language_changed": "Language changed to {lang}",
        "language_set_es": "Language changed to Spanish",
        "language_set_en": "Language changed to English",
        "help_summary": "I can help you with the following: {summary}",
        "help_list": "I can help with: {categories}. Which one do you need?",
        "help_not_found": "Category not found. Say 'help' to see options.",
        "no_match": "I'm not sure I understand. Can you repeat or say 'help'?",
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
        "youtube_search":{"en": ["youtube", "you tube"],     "es": ["youtube", "you tube"]},
        "youtube_play":  {"en": ["play on youtube", "play"], "es": ["reproduce en youtube", "reproducir en youtube"]},
        "open_url":      {"en": ["open website"],            "es": ["abre sitio web", "abre página"]},
    },
    "git_control": {
        "git_status": {"en": ["git status", "get status"], "es": ["git status", "get status"]},
        "git_commit": {"en": ["git commit", "get commit"], "es": ["git commit", "get commit"]},
        "git_push":   {"en": ["git push", "get push"],     "es": ["git push", "get push"]},
        "git_pull":   {"en": ["git pull", "get pull"],     "es": ["git pull", "get pull"]},
        "git_log":    {"en": ["git log", "get log"],       "es": ["git log", "get log"]},
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
        "send_email":  {"en": ["send email", "send mail", "write email", "compose email"],
                       "es": ["envía correo", "enviar correo", "escribe correo", "redactar correo"]},
        "count_email": {"en": ["how many emails"],       "es": ["cuántos correos", "cuantos correos"]},
        "delete_email":{"en": ["delete email", "remove email", "delete mail"],
                       "es": ["borra correo", "eliminar correo", "borrar correo", "elimina correo"]},
        "schedule_email":{"en": ["schedule email", "send later", "program email"],
                         "es": ["programa correo", "programar correo", "enviar después", "envía después"]},
    },
    "calendar": {
        "list_events": {"en": ["what's on my calendar", "my schedule"],
                        "es": ["qué hay en mi calendario", "mi agenda"]},
        "next_event":  {"en": ["what's next"],            "es": ["qué sigue", "que sigue", "próximo evento"]},
        "create_event":{"en": ["create event", "add to calendar"],
                        "es": ["crear evento", "agregar al calendario"]},
    },
    "tab_control": {
        "close_tab":     {"en": ["close tab"],                    "es": ["cerrar pestaña", "cierra pestaña", "cierra la pestaña"]},
        "new_tab":       {"en": ["new tab", "open tab"],          "es": ["nueva pestaña", "abre pestaña", "abrir pestaña", "abre una pestaña"]},
        "duplicate_tab": {"en": ["duplicate tab"],                 "es": ["duplicar pestaña", "duplica pestaña", "duplica la pestaña"]},
        "switch_tab":    {"en": ["switch tab", "tab picker"],     "es": ["cambiar pestaña", "cambia pestaña", "cambia la pestaña", "selector de pestañas", "cambiar de pestaña"]},
        "reopen_tab":    {"en": ["reopen tab", "restore tab"],    "es": ["reabrir pestaña", "reabre pestaña", "restaurar pestaña", "restaura pestaña"]},
        "focus_address": {"en": ["address bar", "go to address"], "es": ["barra de direcciones", "ir a dirección", "ve a la barra de direcciones", "seleccionar barra de direcciones"]},
    },
    "language_control": {
        "toggle_language": {"en": ["switch language", "change language", "toggle language"],
                           "es": ["cambiar idioma", "cambia idioma", "cambiar a español", "cambiar a ingles"]},
        "set_spanish":    {"en": ["switch to spanish", "speak spanish"],
                          "es": ["cambiar a español", "habla español", "pon español"]},
        "set_english":   {"en": ["switch to english", "speak english"],
                         "es": ["cambiar a ingles", "cambiar a inglés", "habla ingles", "habla inglés", "pon ingles", "pon inglés"]},
    },
    "help": {
        "help": {"en": ["help", "what can you do", "commands"],
                "es": ["ayuda", "qué puedes hacer", "comandos", "qué sabes hacer"]},
        "help_category": {"en": ["help with", "tell me about", "info about"],
                         "es": ["ayuda con", "cuéntame de", "información de", "info de"]},
    },
    "chitchat": {
        "greeting": {"en": ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"],
                    "es": ["hola", "buenos días", "buenas tardes", "buenas noches", "hey"]},
        "how_are_you": {"en": ["how are you", "how's it going", "what's up"],
                       "es": ["cómo estás", "qué tal", "cómo vas", "qué hay"]},
        "who_are_you": {"en": ["who are you", "what are you", "your name"],
                       "es": ["quién eres", "qué eres", "cómo te llamas"]},
        "thanks": {"en": ["thank you", "thanks", "appreciate"],
                  "es": ["gracias", "muchas gracias", "te agradezco"]},
        "compliment": {"en": ["good job", "well done", "you're great", "you're the best"],
                      "es": ["bien hecho", "buen trabajo", "eres genial", "eres el mejor"]},
        "insult": {"en": ["you're bad", "you're stupid", "you're slow"],
                  "es": ["eres malo", "eres tonto", "eres lento"]},
        "status": {"en": ["status", "are you working", "you ok"],
                  "es": ["estado", "estás funcionando", "estás bien"]},
        "joke": {"en": ["tell me a joke", "joke", "make me laugh"],
                "es": ["cuéntame un chiste", "chiste", "hazme reír"]},
    },
    "clock": {
        "set_alarm": {"en": ["set alarm", "alarm at", "wake me"],
                     "es": ["poner alarma", "alarma a las", "despiértame"]},
        "cancel_alarm": {"en": ["cancel alarm", "stop alarm", "remove alarm"],
                        "es": ["cancelar alarma", "para alarma", "quitar alarma"]},
        "list_alarms": {"en": ["list alarms", "what alarms", "show alarms"],
                       "es": ["lista alarmas", "qué alarmas", "mostrar alarmas"]},
        "start_timer": {"en": ["timer", "countdown", "set timer"],
                       "es": ["temporizador", "cuenta regresiva", "poner temporizador"]},
        "stop_timer": {"en": ["stop timer", "cancel timer", "cancel countdown"],
                      "es": ["parar temporizador", "cancelar temporizador", "cancelar cuenta"]},
        "start_stopwatch": {"en": ["start stopwatch", "start chrono", "begin stopwatch"],
                           "es": ["iniciar cronómetro", "empezar cronómetro", "iniciar cronometro"]},
        "stop_stopwatch": {"en": ["stop stopwatch", "stop chrono", "pause stopwatch"],
                          "es": ["parar cronómetro", "parar cronometro", "pausar cronómetro"]},
        "reset_stopwatch": {"en": ["reset stopwatch", "reset chrono"],
                           "es": ["reiniciar cronómetro", "reiniciar cronometro"]},
        "read_stopwatch": {"en": ["read stopwatch", "check stopwatch", "what time stopwatch", "elapsed time"],
                          "es": ["leer cronómetro", "ver cronómetro", "qué tiempo cronómetro", "tiempo transcurrido"]},
    },
}

WAKE_PHRASES = {
    "en": ["goodbye", "goodbye jarvis", "bye jarvis", "exit jarvis", "close jarvis"],
    "es": ["adiós", "adios", "adiós jarvis", "adios jarvis", "hasta luego jarvis", "chao jarvis"],
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
