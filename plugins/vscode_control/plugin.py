"""vscode_control plugin - Open projects and control VS Code."""

import subprocess
from pathlib import Path


def init(bus):
    pass


def _run_code(*args, bus, msg="Done"):
    try:
        subprocess.Popen(["code"] + list(args))
        bus.emit("speak", msg)
    except FileNotFoundError:
        bus.emit("speak", "VS Code is not installed or not in PATH")


def handle(action: str, text: str, bus):
    if action == "open_vscode":
        _run_code(bus=bus, msg="Opening VS Code")

    elif action == "open_project":
        name = text.lower().split("open project", 1)[1].strip()
        if not name:
            bus.emit("speak", "Which project should I open?")
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
            _run_code(str(found), bus=bus, msg=f"Opening {found.name}")
        else:
            bus.emit("speak", f"Could not find project {name}")

    elif action == "open_file":
        name = text.lower().split("open file", 1)[1].strip()
        if not name:
            bus.emit("speak", "Which file should I open?")
            return
        _run_code(name, bus=bus, msg=f"Opening {name}")

    elif action == "run_task":
        _run_code(".", bus=bus, msg="Opened VS Code in current directory")
