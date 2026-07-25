"""git_control plugin - Basic git commands via GitPython."""

from pathlib import Path

from git import InvalidGitRepositoryError, Repo

from core.language import resp
from core.text_utils import extract_after_keyword

REPO_PATH = Path.cwd()

_pending_confirm = None


def init(bus):
    pass


def handle(action: str, text: str, bus):
    global _pending_confirm

    if _pending_confirm is not None:
        answer = text.lower().strip()
        if answer in ("sí", "si", "yes", "confirmo", "confirm", "ok", "dale", "claro", "afirmativo"):
            pending = _pending_confirm
            _pending_confirm = None
            _execute_commit(pending["repo"], pending["msg"], pending["count"], bus)
        else:
            _pending_confirm = None
            bus.emit("speak", resp("git_commit_cancelled"))
        return

    try:
        repo = Repo(REPO_PATH, search_parent_directories=True)
    except InvalidGitRepositoryError:
        bus.emit("speak", resp("git_not_repo"))
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
        bus.emit("speak", resp("git_status_result", summary=summary))

    elif action == "git_commit":
        msg = extract_after_keyword(text.lower(), ("git commit", "get commit", "commit"))
        if not msg:
            bus.emit("speak", resp("git_what_commit"))
            return
        changed = [f for f in repo.untracked_files]
        staged = [item.a_path for item in repo.index.diff(None)]
        total_files = len(changed) + len(staged)
        if total_files == 0:
            bus.emit("speak", resp("git_status_result", summary="Clean working tree"))
            return
        _pending_confirm = {"repo": repo, "msg": msg, "count": total_files}
        bus.emit("speak", resp("git_commit_confirm", count=total_files, msg=msg))

    elif action == "git_push":
        try:
            repo.remote().push()
            bus.emit("speak", resp("git_pushed"))
        except Exception as e:
            bus.emit("speak", resp("git_push_failed", error=str(e)))

    elif action == "git_pull":
        try:
            repo.remote().pull()
            bus.emit("speak", resp("git_pulled"))
        except Exception as e:
            bus.emit("speak", resp("git_pull_failed", error=str(e)))

    elif action == "git_log":
        logs = list(repo.iter_commits(max_count=5))
        if logs:
            lines = [f"{c.hexsha[:7]} {c.summary}" for c in logs]
            bus.emit("speak", resp("git_log_result", count=len(logs), log="; ".join(lines)))
        else:
            bus.emit("speak", resp("git_no_commits"))


def _execute_commit(repo, msg: str, count: int, bus):
    repo.index.add([f for f in repo.untracked_files] + [item.a_path for item in repo.index.diff(None)])
    repo.index.commit(msg)
    bus.emit("speak", resp("git_committed", msg=msg))
