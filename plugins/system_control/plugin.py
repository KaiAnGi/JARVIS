"""system_control plugin - Open apps, manage windows, file explorer."""

import os
import subprocess

import pygetwindow as gw


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
        bus.emit("speak", "Abriendo explorador de archivos")
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
        bus.emit("speak", "¿Qué debo abrir?")
        return
    cmd = APPS.get(name, name)
    try:
        subprocess.Popen(cmd, shell=True)
        bus.emit("speak", f"Abriendo {name}")
    except FileNotFoundError:
        bus.emit("speak", f"No pude encontrar {name}")


def _minimize(bus):
    try:
        win = gw.getActiveWindow()
        if win:
            win.minimize()
            bus.emit("speak", "Ventana minimizada")
        else:
            bus.emit("speak", "No hay ventana activa")
    except Exception:
        bus.emit("speak", "No pude minimizar la ventana")


def _maximize(bus):
    try:
        win = gw.getActiveWindow()
        if win:
            if win.isMaximized:
                win.restore()
                bus.emit("speak", "Ventana restaurada")
            else:
                win.maximize()
                bus.emit("speak", "Ventana maximizada")
        else:
            bus.emit("speak", "No hay ventana activa")
    except Exception:
        bus.emit("speak", "No pude cambiar la ventana")


def _close(bus):
    try:
        win = gw.getActiveWindow()
        if win:
            win.close()
            bus.emit("speak", "Ventana cerrada")
        else:
            bus.emit("speak", "No hay ventana activa")
    except Exception:
        bus.emit("speak", "No pude cerrar la ventana")
