"""File hardening helpers (Windows ACL restriction)."""

import os
import subprocess
from pathlib import Path


def restrict_file(path: Path):
    """Restrict a file so only the current user can read/write it (Windows).

    Uses icacls to strip inherited ACLs and grant full control to the
    current user only. No-op on non-Windows or if the file is missing.
    """
    if os.name != "nt" or not path.exists():
        return

    user = os.environ.get("USERNAME", "")
    if not user:
        return

    cmd = ["icacls", str(path), "/inheritance:r", "/grant:r", f"{user}:F"]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=10)
    except Exception:
        pass
