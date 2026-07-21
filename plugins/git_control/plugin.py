"""git_control plugin - Basic git commands via GitPython."""

import subprocess
from pathlib import Path

from git import Repo, InvalidGitRepositoryError


REPO_PATH = Path.cwd()


def init(bus):
    pass


def handle(action: str, text: str, bus):
    try:
        repo = Repo(REPO_PATH, search_parent_directories=True)
    except InvalidGitRepositoryError:
        bus.emit("speak", "Not inside a git repository")
        return

    if action == "git_status":
        changed = [item.a_path for item in repo.index.diff(None)]
        untracked = repo.untracked_files
        parts = []
        if changed:
            parts.append(f"{len(changed)} changed files")
        if untracked:
            parts.append(f"{len(untracked)} untracked files")
        summary = ", ".join(parts) if parts else "Clean working tree"
        bus.emit("speak", f"Git status: {summary}")

    elif action == "git_commit":
        msg = text.lower()
        for prefix in ("git commit", "commit"):
            if prefix in msg:
                msg = msg.split(prefix, 1)[1].strip()
                break
        if not msg:
            bus.emit("speak", "What should the commit message be?")
            return
        repo.index.add([f for f in repo.untracked_files] +
                       [item.a_path for item in repo.index.diff(None)])
        repo.index.commit(msg)
        bus.emit("speak", f"Committed: {msg}")

    elif action == "git_push":
        try:
            repo.remote().push()
            bus.emit("speak", "Pushed to remote")
        except Exception as e:
            bus.emit("speak", f"Push failed: {e}")

    elif action == "git_pull":
        try:
            repo.remote().pull()
            bus.emit("speak", "Pulled from remote")
        except Exception as e:
            bus.emit("speak", f"Pull failed: {e}")

    elif action == "git_log":
        logs = list(repo.iter_commits(max_count=5))
        if logs:
            lines = [f"{c.hexsha[:7]} {c.summary}" for c in logs]
            bus.emit("speak", f"Last {len(logs)} commits: {'; '.join(lines)}")
        else:
            bus.emit("speak", "No commits found")
