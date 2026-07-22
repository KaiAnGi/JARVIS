"""language_control plugin - Switch language via voice."""

from core.language import toggle_lang, set_lang, get_lang, resp


def init(bus):
    pass


def handle(action: str, text: str, bus):
    if action == "toggle_language":
        new_lang = toggle_lang()
        bus.emit("language_changed", new_lang)
        lang_name = "Español" if new_lang == "es" else "English"
        bus.emit("speak", resp("language_changed", lang=lang_name))

    elif action == "set_spanish":
        if get_lang() != "es":
            new_lang = toggle_lang()
            bus.emit("language_changed", new_lang)
        bus.emit("speak", resp("language_set_es"))

    elif action == "set_english":
        if get_lang() != "en":
            new_lang = toggle_lang()
            bus.emit("language_changed", new_lang)
        bus.emit("speak", resp("language_set_en"))
