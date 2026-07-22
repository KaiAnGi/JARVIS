"""Clipboard plugin — copy, paste, read clipboard content."""

import pyperclip
from core.language import resp


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
                import pyperclip as pc
                pc.copy(content)
                import pyautogui
                pyautogui.hotkey("ctrl", "v")
                bus.emit("speak", resp("clipboard_pasted"))
            else:
                bus.emit("speak", resp("clipboard_empty"))
        except Exception:
            bus.emit("speak", resp("clipboard_error"))


def _extract_text(text: str, keywords: tuple) -> str:
    lower = text.lower()
    for kw in keywords:
        idx = lower.find(kw)
        if idx != -1:
            after = text[idx + len(kw):].strip()
            if after:
                return after
    return ""
