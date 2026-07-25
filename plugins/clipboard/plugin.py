"""Clipboard plugin — copy, paste, read clipboard content."""

import pyperclip

from core.language import resp
from core.text_utils import extract_after_keyword


def init(bus):
    pass


def handle(action: str, text: str, bus):
    if action == "clipboard_read":
        try:
            content = pyperclip.paste()
            if content:
                bus.emit("speak", resp("clipboard_content", content=content[:200]))
            else:
                bus.emit("speak", resp("clipboard_empty"))
        except Exception:
            bus.emit("speak", resp("clipboard_error"))

    elif action == "clipboard_copy":
        text_to_copy = _extract_text(text, ("copy", "copiar", "clona"))
        if text_to_copy:
            try:
                pyperclip.copy(text_to_copy)
                bus.emit("speak", resp("clipboard_copied"))
            except Exception:
                bus.emit("speak", resp("clipboard_error"))
        else:
            bus.emit("speak", resp("clipboard_copy_what"))

    elif action == "clipboard_paste":
        try:
            content = pyperclip.paste()
            if content:
                import pyautogui

                pyautogui.hotkey("ctrl", "v")
                bus.emit("speak", resp("clipboard_pasted"))
            else:
                bus.emit("speak", resp("clipboard_empty"))
        except Exception:
            bus.emit("speak", resp("clipboard_error"))


def _extract_text(text: str, keywords: tuple) -> str:
    return extract_after_keyword(text, keywords)
