"""system_control plugin - Open apps, manage windows, file explorer."""

import os
import subprocess

import pygetwindow as gw

from core.language import resp

APPS = {
    "notepad": "notepad", "bloc de notas": "notepad",
    "calculator": "calc", "calc": "calc", "calculadora": "calc",
    "paint": "mspaint", "mspaint": "mspaint",
    "explorer": "explorer", "file explorer": "explorer", "explorador": "explorador de archivos": "explorer",
    "task manager": "taskmgr", "administrador de tareas": "taskmgr",
    "terminal": "wt", "powershell": "pwsh", "cmd": "cmd",
    "wordpad": "write",
    "word": r"***REMOVED***",
    "microsoft word": r"***REMOVED***",
    "excel": r"***REMOVED***",
    "microsoft excel": r"***REMOVED***",
    "powerpoint": r"***REMOVED***",
    "microsoft powerpoint": r"***REMOVED***",
    "visual studio code": os.path.expandvars(r"***REMOVED***"),
    "vs code": os.path.expandvars(r"***REMOVED***"),
    "chrome": r"***REMOVED***",
    "google chrome": r"***REMOVED***",
    "steam": r"***REMOVED***",
    "epic games": r"***REMOVED***",
    "epic": r"***REMOVED***",
    "ea": r"***REMOVED***",
    "ea app": r"***REMOVED***",
    "overwolf": r"***REMOVED***",
    "discord": os.path.expandvars(r"***REMOVED***"),
    "fivem": os.path.expandvars(r"***REMOVED***"),
    "osu": os.path.expandvars(r"***REMOVED***"),
    "osu!": os.path.expandvars(r"***REMOVED***"),
    "genshin impact": "https://shop.hoyoverse.com/genshin",
    "genshin": "https://shop.hoyoverse.com/genshin",
    "los sims 4": "https://www.ea.com/es-es/games/the-sims/the-sims-4",
    "sims 4": "https://www.ea.com/es-es/games/the-sims/the-sims-4",
    "sims": "https://www.ea.com/es-es/games/the-sims/the-sims-4",
    "valorant": "https://playvalorant.com/",
    "rockstar": r"***REMOVED***",
    "rockstar games": r"***REMOVED***",
    "winrar": r"***REMOVED***",
    "minecraft": r"***REMOVED***",
    "unity": r"***REMOVED***",
    "unity hub": r"***REMOVED***",
    "intellij": r"***REMOVED***",
    "intellij idea": r"***REMOVED***",
    "openoffice": r"***REMOVED***",
    "obs": r"***REMOVED***",
    "obs studio": r"***REMOVED***",
    "edge": "msedge",
    "microsoft edge": "msedge",
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

    for article in ("el ", "la ", "los ", "las ", "un ", "una "):
        if name.startswith(article):
            name = name[len(article):]
            break

    if not name:
        bus.emit("speak", resp("what_open"))
        return

    cmd = APPS.get(name, name)

    if cmd.startswith("http"):
        import webbrowser
        webbrowser.open(cmd)
        bus.emit("speak", resp("open_app", name=name))
        return

    if os.path.isfile(cmd):
        try:
            subprocess.Popen([cmd])
            bus.emit("speak", resp("open_app", name=name))
        except Exception:
            bus.emit("speak", resp("open_fail", name=name))
        return

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
