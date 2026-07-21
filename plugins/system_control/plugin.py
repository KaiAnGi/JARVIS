"""system_control plugin - Open apps, manage windows, file explorer."""

import subprocess

import pygetwindow as gw

from core.language import resp

APPS = {
    "notepad": "notepad", "bloc de notas": "notepad",
    "calculator": "calc", "calc": "calc", "calculadora": "calc",
    "paint": "mspaint", "mspaint": "mspaint",
    "explorer": "explorer", "file explorer": "explorer", "explorador": "explorer",
    "task manager": "taskmgr", "administrador de tareas": "taskmgr",
    "terminal": "wt", "powershell": "pwsh", "cmd": "cmd",
    "wordpad": "write",
}


def init(bus):
    pass


def handle(action: str, text: str, bus):
    if action == "open_app":
        _open_app(text, bus)
    elif action == "open_explorer":
        subprocess.Popen(["explorer"])
        bus.emit("speak", resp("open_explorer"))
    elif action == "minimize_window":
        _minimize(bus)
    elif action == "maximize_window":
        _maximize(bus)
    elif action == "close_window":
        _close(bus)


def _open_app(text: str, bus):
    name = text.lower()
    for prefix in ("open", "launch", "abre", "iniciar"):
        if prefix in name:
            name = name.split(prefix, 1)[1]
            break
    name = name.strip()
    if not name:
        bus.emit("speak", resp("what_open"))
        return
    cmd = APPS.get(name, name)
    try:
        subprocess.Popen(cmd, shell=True)
        bus.emit("speak", resp("open_app", name=name))
    except FileNotFoundError:
        bus.emit("speak", resp("open_fail", name=name))


def _minimize(bus):
    try:
        win = gw.getActiveWindow()
        if win:
            win.minimize()
            bus.emit("speak", resp("minimized"))
        else:
            bus.emit("speak", resp("no_window"))
    except Exception:
        bus.emit("speak", resp("min_error"))


def _maximize(bus):
    try:
        win = gw.getActiveWindow()
        if win:
            if win.isMaximized:
                win.restore()
                bus.emit("speak", resp("restored"))
            else:
                win.maximize()
                bus.emit("speak", resp("maximized"))
        else:
            bus.emit("speak", resp("no_window"))
    except Exception:
        bus.emit("speak", resp("max_error"))


def _close(bus):
    try:
        win = gw.getActiveWindow()
        if win:
            win.close()
            bus.emit("speak", resp("closed"))
        else:
            bus.emit("speak", resp("no_window"))
    except Exception:
        bus.emit("speak", resp("close_error"))
