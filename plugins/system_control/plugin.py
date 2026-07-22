"""system_control plugin - Open apps, manage windows, file explorer."""

import os
import subprocess

import pygetwindow as gw

from core.language import resp

APPS = {
    "notepad": "notepad", "bloc de notas": "notepad",
    "calculator": "calc", "calc": "calc", "calculadora": "calc",
    "paint": "mspaint", "mspaint": "mspaint",
    "explorer": "explorer", "file explorer": "explorer", "explorador": "explorer", "explorador de archivos": "explorer", "browser": r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe", "navegador": r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "task manager": "taskmgr", "administrador de tareas": "taskmgr",
    "terminal": "wt", "powershell": "pwsh", "cmd": "cmd",
    "wordpad": "write",
    "word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    "microsoft word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    "excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
    "microsoft excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
    "powerpoint": r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
    "microsoft powerpoint": r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
    "visual studio code": os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"),
    "vs code": os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"),
    "chrome": r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "google chrome": r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "steam": r"C:\Program Files (x86)\Steam\steam.exe",
    "epic games": r"C:\Program Files (x86)\Epic Games\Launcher\Engine\Binaries\Win64\EpicGamesLauncher.exe",
    "epic": r"C:\Program Files (x86)\Epic Games\Launcher\Engine\Binaries\Win64\EpicGamesLauncher.exe",
    "ea": r"C:\Program Files\Electronic Arts\EA Desktop\EA Desktop\EADesktop.exe",
    "ea app": r"C:\Program Files\Electronic Arts\EA Desktop\EA Desktop\EADesktop.exe",
    "overwolf": r"C:\Program Files (x86)\Overwolf\OverwolfLauncher.exe",
    "discord": os.path.expandvars(r"%LOCALAPPDATA%\Discord\app-1.0.9248\Discord.exe"),
    "fivem": os.path.expandvars(r"%LOCALAPPDATA%\FiveM\FiveM.exe"),
    "osu": os.path.expandvars(r"%LOCALAPPDATA%\osu!\osu!.exe"),
    "osu!": os.path.expandvars(r"%LOCALAPPDATA%\osu!\osu!.exe"),
    "genshin impact": "https://shop.hoyoverse.com/genshin",
    "genshin": "https://shop.hoyoverse.com/genshin",
    "los sims 4": "https://www.ea.com/es-es/games/the-sims/the-sims-4",
    "sims 4": "https://www.ea.com/es-es/games/the-sims/the-sims-4",
    "sims": "https://www.ea.com/es-es/games/the-sims/the-sims-4",
    "valorant": "https://playvalorant.com/",
    "rockstar": r"C:\Program Files\Rockstar Games\Launcher\Launcher.exe",
    "rockstar games": r"C:\Program Files\Rockstar Games\Launcher\Launcher.exe",
    "winrar": r"C:\Program Files\WinRAR\WinRAR.exe",
    "minecraft": r"C:\Program Files\Minecraft Launcher\MinecraftLauncher.exe",
    "unity": r"C:\Program Files\Unity Hub\Unity Hub.exe",
    "unity hub": r"C:\Program Files\Unity Hub\Unity Hub.exe",
    "intellij": r"C:\Program Files\JetBrains\IntelliJ IDEA 2025.1.2\bin\idea64.exe",
    "intellij idea": r"C:\Program Files\JetBrains\IntelliJ IDEA 2025.1.2\bin\idea64.exe",
    "openoffice": r"C:\Program Files\OpenOffice 4\program\soffice.exe",
    "obs": r"C:\Program Files\obs-studio\bin\64bit\obs64.exe",
    "obs studio": r"C:\Program Files\obs-studio\bin\64bit\obs64.exe",
    "edge": "msedge",
    "microsoft edge": "msedge",
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

    cmd = APPS.get(name)

    if cmd is None:
        bus.emit("speak", resp("open_fail", name=name))
        return

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
