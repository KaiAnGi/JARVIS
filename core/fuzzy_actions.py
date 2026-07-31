"""Map LLM-produced action JSON to router plugin calls.

This is the security allowlist for fuzzy intent: only actions in
``_PLUGIN_MAP`` can be executed, and each one is rewritten into a known
text command for an existing plugin. Nothing arbitrary is ever run.
"""

from core.language import resp

_PLUGIN_MAP = {
    "open_app": "system_control",
    "minimize_window": "system_control",
    "maximize_window": "system_control",
    "close_window": "system_control",
    "web_search": "browser",
    "youtube_search": "browser",
    "check_email": "gmail",
    "read_email": "gmail",
    "count_email": "gmail",
    "list_events": "calendar",
    "next_event": "calendar",
    "get_time": "datetime_calc",
    "get_date": "datetime_calc",
    "calculate": "datetime_calc",
    "set_alarm": "clock",
    "start_timer": "clock",
    "start_stopwatch": "clock",
    "stop_stopwatch": "clock",
    "read_stopwatch": "clock",
    "reset_stopwatch": "clock",
    "git_status": "git_control",
    "git_commit": "git_control",
    "git_push": "git_control",
    "git_pull": "git_control",
    "close_tab": "tab_control",
    "new_tab": "tab_control",
    "duplicate_tab": "tab_control",
    "last_command": "command_history",
    "command_history": "command_history",
    "clear_history": "command_history",
    "help": "help",
}

_STATIC_TEXT = {
    "check_email": "check email",
    "read_email": "read email",
    "count_email": "how many emails",
    "list_events": "what's on my calendar",
    "next_event": "what's next",
    "get_time": "what time",
    "get_date": "what date",
    "minimize_window": "minimize",
    "maximize_window": "maximize",
    "close_window": "close window",
    "start_stopwatch": "start stopwatch",
    "stop_stopwatch": "stop stopwatch",
    "read_stopwatch": "read stopwatch",
    "reset_stopwatch": "reset stopwatch",
    "git_status": "git status",
    "git_push": "git push",
    "git_pull": "git pull",
    "close_tab": "close tab",
    "new_tab": "new tab",
    "duplicate_tab": "duplicate tab",
    "last_command": "last command",
    "command_history": "command history",
    "clear_history": "clear history",
    "help": "help",
}


def _build_alarm_text(action: dict) -> str:
    text = f"set alarm at {action.get('time', '')}"
    rep = action.get("repetition", "none")
    msg = action.get("message", "")
    if rep != "none":
        text += f" {rep}"
    if msg:
        text += f" message {msg}"
    return text


_PARAM_BUILDERS = {
    "open_app": lambda a: f"open {a.get('app', '')}",
    "web_search": lambda a: f"search for {a.get('query', '')}",
    "youtube_search": lambda a: f"youtube {a.get('query', '')}",
    "calculate": lambda a: f"calculate {a.get('expression', '')}",
    "git_commit": lambda a: f"git commit {a.get('message', '')}",
    "set_alarm": _build_alarm_text,
    "start_timer": lambda a: f"timer for {a.get('duration', '5')} {a.get('unit', 'minutes')}",
}


def execute_fuzzy_action(action: dict, router, bus) -> bool:
    """Execute an LLM-returned action through the router. Returns True if handled.

    ``router`` only needs a ``get_plugin(name)`` method.
    """
    name = action.get("action", "")
    if not name or name == "unknown":
        bus.emit("speak", resp("no_match"))
        return False

    plugin_name = _PLUGIN_MAP.get(name)
    if plugin_name is None:
        bus.emit("speak", resp("no_match"))
        return False

    plugin = router.get_plugin(plugin_name)
    if plugin is None:
        bus.emit("speak", resp("no_match"))
        return False

    text = _PARAM_BUILDERS.get(name, lambda a: _STATIC_TEXT.get(name, ""))(action)
    plugin.handle(name, text, bus)
    return True
