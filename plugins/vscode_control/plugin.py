"""vscode_control plugin - Open projects and control VS Code."""

import subprocess
from pathlib import Path


def init(bus):
    pass


def handle(action: str, text: str, bus):
    if action == "open_vscode":
        subprocess.Popen(["code"], shell=True)
        bus.emit("speak", "Opening VS Code")

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
            subprocess.Popen(["code", str(found)])
            bus.emit("speak", f"Opening {found.name}")
        else:
            bus.emit("speak", f"Could not find project {name}")

    elif action == "open_file":
        name = text.lower().split("open file", 1)[1].strip()
        if not name:
            bus.emit("speak", "Which file should I open?")
            return
        code_cmd = ["code"] + [name]
        subprocess.Popen(code_cmd)
        bus.emit("speak", f"Opening {name}")

    elif action == "run_task":
        subprocess.Popen(["code", "."])
        bus.emit("speak", "Opened VS Code in current directory")
