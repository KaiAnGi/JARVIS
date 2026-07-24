"""vscode_control plugin - Open projects and control VS Code."""

import os
import shutil
import subprocess
from pathlib import Path

from core.language import resp


def init(bus):
    pass


def _find_code_exe():
    code_path = shutil.which("code")
    if code_path:
        return code_path
    for p in [
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"),
        r"C:\Program Files\Microsoft VS Code\Code.exe",
        r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",
    ]:
        if os.path.isfile(p):
            return p
    return None


def _run_code(*args, bus, msg_key="vscode_opened", **msg_kwargs):
    try:
        subprocess.Popen(["code"] + list(args))
        bus.emit("speak", resp(msg_key, **msg_kwargs) if msg_kwargs else resp(msg_key))
    except FileNotFoundError:
        exe = _find_code_exe()
        if exe:
            try:
                subprocess.Popen([exe] + list(args))
                bus.emit("speak", resp(msg_key, **msg_kwargs) if msg_kwargs else resp(msg_key))
            except Exception:
                bus.emit("speak", resp("vscode_not_found"))
        else:
            bus.emit("speak", resp("vscode_not_found"))


def handle(action: str, text: str, bus):
    if action == "open_vscode":
        _run_code(bus=bus)

    elif action == "open_project":
        name = text.lower().split("open project", 1)[1].strip()
        if not name:
            bus.emit("speak", resp("vscode_what_project"))
            return
        search_dirs = [
            Path.home() / "Documents",
            Path.home() / "Projects",
            Path.home() / "Dev",
            Path.home() / "repos",
            Path.home(),
        ]
        found = None
        for base in search_dirs:
            if not base.exists():
                continue
            for d in base.iterdir():
                if d.is_dir() and name.lower() in d.name.lower():
                    found = d
                    break
            if found:
                break
        if found:
            _run_code(str(found), bus=bus, msg_key="vscode_opening", name=found.name)
        else:
            bus.emit("speak", resp("vscode_project_not_found", name=name))

    elif action == "open_file":
        name = text.lower().split("open file", 1)[1].strip()
        if not name:
            bus.emit("speak", resp("vscode_what_file"))
            return
        _run_code(name, bus=bus, msg_key="vscode_opening", name=name)

    elif action == "run_task":
        _run_code(".", bus=bus, msg_key="vscode_opened_dir")
