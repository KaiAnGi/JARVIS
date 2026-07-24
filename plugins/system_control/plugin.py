"""system_control plugin - Open apps, manage windows, file explorer."""

import os
import shutil
import subprocess

import pygetwindow as gw

from core.language import resp

APPS = {
    "notepad": "notepad", "bloc de notas": "notepad",
    "calculator": "calc", "calc": "calc", "calculadora": "calc",
    "paint": "mspaint", "mspaint": "mspaint",
    "explorer": "explorer", "file explorer": "explorer",
    "explorador": "explorer", "explorador de archivos": "explorer",
    "task manager": "taskmgr", "administrador de tareas": "taskmgr",
    "terminal": "wt", "powershell": "pwsh", "cmd": "cmd",
    "wordpad": "write",
    "edge": "msedge", "microsoft edge": "msedge",
    "discord": "discord",
    "obs": "obs64", "obs studio": "obs64",
    "winrar": "WinRAR",
}

APPS_PATH = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "google chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "browser": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "navegador": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    "microsoft word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    "excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
    "microsoft excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
    "powerpoint": r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
    "microsoft powerpoint": r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
}

APPS_URL = {
    "whatsapp": "https://web.whatsapp.com",
    "whatsapp web": "https://web.whatsapp.com",
    "spotify": "https://open.spotify.com",
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

    if name in APPS_URL:
        import webbrowser
        webbrowser.open(APPS_URL[name])
        bus.emit("speak", resp("open_app", name=name))
        return

    if name in APPS:
        cmd = APPS[name]
        which = shutil.which(cmd)
        if which:
            try:
                subprocess.Popen([which])
                bus.emit("speak", resp("open_app", name=name))
            except Exception:
                bus.emit("speak", resp("open_fail", name=name))
            return
        if os.path.isfile(cmd):
            try:
                subprocess.Popen([cmd])
                bus.emit("speak", resp("open_app", name=name))
            except Exception:
                bus.emit("speak", resp("open_fail", name=name))
            return

    if name in APPS_PATH:
        cmd = APPS_PATH[name]
        if os.path.isfile(cmd):
            try:
                subprocess.Popen([cmd])
                bus.emit("speak", resp("open_app", name=name))
            except Exception:
                bus.emit("speak", resp("open_fail", name=name))
            return

    which = shutil.which(name)
    if which:
        try:
            subprocess.Popen([which])
            bus.emit("speak", resp("open_app", name=name))
            return
        except Exception:
            pass

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
