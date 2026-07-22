"""tab_control plugin - Browser tab management via keyboard shortcuts."""

import time

import pyautogui
import pygetwindow as gw

from core.language import resp

pyautogui.PAUSE = 0.1
pyautogui.FAILSAFE = True

BROWSERS = ["chrome", "edge", "brave", "opera", "mozilla firefox"]


def init(bus):
    pass


def _is_browser_active() -> bool:
    win = gw.getActiveWindow()
    if not win:
        return False
    title = win.title.lower()
    if any(b in title for b in BROWSERS):
        return True
    try:
        windows = gw.getAllWindows()
        for w in windows:
            if w.title and any(b in w.title.lower() for b in BROWSERS):
                return True
    except Exception:
        pass
    return False


def _focus_browser() -> bool:
    try:
        windows = gw.getAllWindows()
        for w in windows:
            if w.title and any(b in w.title.lower() for b in BROWSERS):
                w.activate()
                time.sleep(0.2)
                return True
    except Exception:
        pass
    return False


def handle(action: str, text: str, bus):
    if not _is_browser_active():
        bus.emit("speak", resp("no_browser"))
        return

    try:
        _focus_browser()

        if action == "close_tab":
            pyautogui.hotkey("ctrl", "w")
            time.sleep(0.15)
            bus.emit("speak", resp("tab_closed"))

        elif action == "new_tab":
            pyautogui.hotkey("ctrl", "t")
            time.sleep(0.15)
            bus.emit("speak", resp("tab_new"))

        elif action == "duplicate_tab":
            pyautogui.hotkey("ctrl", "l")
            time.sleep(0.1)
            pyautogui.hotkey("ctrl", "c")
            time.sleep(0.1)
            pyautogui.hotkey("ctrl", "t")
            time.sleep(0.15)
            pyautogui.hotkey("ctrl", "v")
            time.sleep(0.1)
            pyautogui.press("enter")
            time.sleep(0.15)
            bus.emit("speak", resp("tab_duplicated"))

        elif action == "switch_tab":
            pyautogui.hotkey("ctrl", "shift", "a")
            time.sleep(0.2)
            bus.emit("speak", resp("tab_switched"))

        elif action == "reopen_tab":
            pyautogui.hotkey("ctrl", "shift", "t")
            time.sleep(0.15)
            bus.emit("speak", resp("tab_reopened"))

        elif action == "focus_address":
            pyautogui.hotkey("ctrl", "l")
            time.sleep(0.1)
            bus.emit("speak", resp("address_focused"))

    except Exception:
        bus.emit("speak", resp("tab_error"))
