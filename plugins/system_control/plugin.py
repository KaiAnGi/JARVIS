"""system_control plugin - Open apps, manage windows, file explorer."""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pygetwindow as gw

from core.language import resp

APPS = {
    "notepad": "notepad",
    "bloc de notas": "notepad",
    "calculator": "calc",
    "calc": "calc",
    "calculadora": "calc",
    "paint": "mspaint",
    "mspaint": "mspaint",
    "explorer": "explorer",
    "file explorer": "explorer",
    "explorador": "explorer",
    "explorador de archivos": "explorer",
    "task manager": "taskmgr",
    "administrador de tareas": "taskmgr",
    "terminal": "wt",
    "powershell": "pwsh",
    "cmd": "cmd",
    "wordpad": "write",
    "edge": "msedge",
    "microsoft edge": "msedge",
    "discord": "discord",
    "obs": "obs64",
    "obs studio": "obs64",
    "winrar": "WinRAR",
}

APPS_PATH = {
    "chrome": r"***REMOVED***",
    "google chrome": r"***REMOVED***",
    "browser": r"***REMOVED***",
    "navegador": r"***REMOVED***",
    "word": r"***REMOVED***",
    "microsoft word": r"***REMOVED***",
    "excel": r"***REMOVED***",
    "microsoft excel": r"***REMOVED***",
    "powerpoint": r"***REMOVED***",
    "microsoft powerpoint": r"***REMOVED***",
}

BROWSER_CANDIDATES = (
    r"***REMOVED***",
    r"***REMOVED***",
)

BROWSER_NAMES = ("browser", "navegador", "chrome", "google chrome")

APPS_URL = {
    "whatsapp": "https://web.whatsapp.com",
    "whatsapp web": "https://web.whatsapp.com",
    "spotify": "https://open.spotify.com",
}

USER_APPS_PATH = Path(__file__).resolve().parent.parent.parent / "config" / "user_apps.json"
_user_apps: dict[str, dict] = {"apps": {}, "urls": {}}

APP_ALIASES = {
    "what that": "wattpad",
    "what but": "wattpad",
    "what tap": "wattpad",
    "what bad": "wattpad",
    "what pad": "wattpad",
    "what pads": "wattpad",
    "gen shin": "genshin",
    "jen shin": "genshin",
    "genshin impact": "genshin",
    "hoyo play": "hoyoplay",
    "oyo play": "hoyoplay",
    "five m": "fivem",
    "5 m": "fivem",
    "this court": "discord",
    "this card": "discord",
    "disk or": "discord",
    "ob s": "obs",
    "o b s": "obs",
    "over wolf": "overwolf",
    "over walk": "overwolf",
    "ld player": "ldplayer",
    "el de player": "ldplayer",
    "mic tech": "miktex",
    "my tech": "miktex",
    "u torrent": "utorrent",
    "you torrent": "utorrent",
    "rock star": "rockstar",
    "oh sue": "osu",
    "o s u": "osu",
}


def _load_user_apps():
    """Load user-specific app paths from config/user_apps.json."""
    global _user_apps
    if not USER_APPS_PATH.exists():
        return
    try:
        data = json.loads(USER_APPS_PATH.read_text(encoding="utf-8"))
        _user_apps["apps"].update(data.get("apps", {}))
        _user_apps["urls"].update(data.get("urls", {}))
    except (json.JSONDecodeError, OSError) as e:
        print(f"[SYSTEM_CONTROL] Failed to load user_apps.json: {e}")


def _resolve_name(name: str) -> str:
    """Resolve phonetic misrecognitions and aliases to canonical app name."""
    if name in APP_ALIASES:
        return APP_ALIASES[name]
    for alias, canonical in APP_ALIASES.items():
        if alias in name:
            return canonical
    return name


def init(bus):
    _load_user_apps()


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


def _clean_app_name(text: str) -> str:
    """Strip command prefixes and articles from the spoken app name."""
    name = text.lower()
    for prefix in ("open", "launch", "abre", "iniciar"):
        if prefix in name:
            name = name.split(prefix, 1)[1]
            break
    name = name.strip()
    for article in ("el ", "la ", "los ", "las ", "un ", "una "):
        if name.startswith(article):
            name = name[len(article) :]
            break
    return name.strip()


def _launch(name: str, cmd: str, bus) -> bool:
    """Launch a process. Emits success/failure. Returns True on success."""
    try:
        subprocess.Popen([cmd])
        bus.emit("speak", resp("open_app", name=name))
        return True
    except Exception:
        bus.emit("speak", resp("open_fail", name=name))
        return False


def _open_url(name: str, url: str, bus) -> bool:
    import webbrowser

    webbrowser.open(url)
    bus.emit("speak", resp("open_app", name=name))
    return True


def _open_browser(name: str, bus) -> bool:
    """Open the browser, trying known Chrome paths then the OS default."""
    for candidate in BROWSER_CANDIDATES:
        if os.path.isfile(candidate):
            return _launch(name, candidate, bus)
    import webbrowser

    webbrowser.open("https://www.google.com")
    bus.emit("speak", resp("open_app", name=name))
    return True


def _open_app(text: str, bus):
    name = _clean_app_name(text)
    if not name:
        bus.emit("speak", resp("what_open"))
        return

    name = _resolve_name(name)

    if name in BROWSER_NAMES and _open_browser(name, bus):
        return

    if name in APPS_URL:
        _open_url(name, APPS_URL[name], bus)
        return

    if name in APPS:
        cmd = APPS[name]
        which = shutil.which(cmd)
        if which:
            _launch(name, which, bus)
            return
        if os.path.isfile(cmd):
            _launch(name, cmd, bus)
            return

    if name in APPS_PATH and os.path.isfile(APPS_PATH[name]):
        _launch(name, APPS_PATH[name], bus)
        return

    if name in _user_apps["urls"]:
        _open_url(name, _user_apps["urls"][name], bus)
        return

    if name in _user_apps["apps"]:
        cmd = _user_apps["apps"][name]
        if cmd.startswith("http"):
            _open_url(name, cmd, bus)
            return
        if os.path.isfile(cmd):
            _launch(name, cmd, bus)
            return

    which = shutil.which(name)
    if which:
        _launch(name, which, bus)
        return

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
