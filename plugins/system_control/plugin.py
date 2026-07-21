"""system_control plugin - Open apps, manage windows, file explorer."""

import os
import subprocess

import pygetwindow as gw


APPS = {
    "notepad": "notepad",
    "calculator": "calc",
    "calc": "calc",
    "paint": "mspaint",
    "mspaint": "mspaint",
    "explorer": "explorer",
    "file explorer": "explorer",
    "task manager": "taskmgr",
    "terminal": "wt",
    "powershell": "pwsh",
    "cmd": "cmd",
    "cmd prompt": "cmd",
    "wordpad": "write",
}


def init(bus):
    pass


def handle(action: str, text: str, bus):
    if action == "open_app":
        _open_app(text, bus)
    elif action == "open_explorer":
        subprocess.Popen(["explorer"])
        bus.emit("speak", "Opening file explorer")
    elif action == "minimize_window":
        _minimize(bus)
    elif action == "maximize_window":
        _maximize(bus)
    elif action == "close_window":
        _close(bus)


def _open_app(text: str, bus):
    name = text.lower()
    for prefix in ("open", "launch"):
        if prefix in name:
            name = name.split(prefix, 1)[1]
            break
    name = name.strip()
    if not name:
        bus.emit("speak", "What should I open?")
        return
    cmd = APPS.get(name, name)
    try:
        subprocess.Popen(cmd, shell=True)
        bus.emit("speak", f"Opening {name}")
    except FileNotFoundError:
        bus.emit("speak", f"I couldn't find {name}")


def _minimize(bus):
    try:
        win = gw.getActiveWindow()
        if win:
            win.minimize()
            bus.emit("speak", "Window minimized")
        else:
            bus.emit("speak", "No active window found")
    except Exception:
        bus.emit("speak", "Couldn't minimize the window")


def _maximize(bus):
    try:
        win = gw.getActiveWindow()
        if win:
            if win.isMaximized:
                win.restore()
                bus.emit("speak", "Window restored")
            else:
                win.maximize()
                bus.emit("speak", "Window maximized")
        else:
            bus.emit("speak", "No active window found")
    except Exception:
        bus.emit("speak", "Couldn't change the window")


def _close(bus):
    try:
        win = gw.getActiveWindow()
        if win:
            win.close()
            bus.emit("speak", "Window closed")
        else:
            bus.emit("speak", "No active window found")
    except Exception:
        bus.emit("speak", "Couldn't close the window")
