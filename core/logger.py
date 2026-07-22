"""Persistent text logging to daily log files."""

import os
import time
from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent / "data" / "logs"


def _get_log_path(date: datetime = None) -> Path:
    """Get the log file path for a given date (default: today)."""
    if date is None:
        date = datetime.now()
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    return LOG_DIR / f"jarvis_{date.strftime('%Y-%m-%d')}.log"


def log_event(sender: str, text: str, event_type: str = "INFO"):
    """Log an event to today's log file."""
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] [{event_type}] [{sender}] {text}\n"
    path = _get_log_path()
    with open(path, "a", encoding="utf-8") as f:
        f.write(line)


def log_command(action: str, parameters: str = "", success: bool = True, duration_ms: float = 0):
    """Log a command execution."""
    ts = datetime.now().strftime("%H:%M:%S")
    status = "OK" if success else "FAIL"
    line = f"[{ts}] [CMD] [{status}] {action}"
    if parameters:
        line += f" | {parameters}"
    if duration_ms:
        line += f" | {duration_ms:.0f}ms"
    line += "\n"
    path = _get_log_path()
    with open(path, "a", encoding="utf-8") as f:
        f.write(line)


def log_error(component: str, error: str):
    """Log an error."""
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] [ERROR] [{component}] {error}\n"
    path = _get_log_path()
    with open(path, "a", encoding="utf-8") as f:
        f.write(line)


def log_session_start():
    """Log session start."""
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] [SESSION] === Session started ===\n"
    path = _get_log_path()
    with open(path, "a", encoding="utf-8") as f:
        f.write(line)


def log_session_end():
    """Log session end."""
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] [SESSION] === Session ended ===\n"
    path = _get_log_path()
    with open(path, "a", encoding="utf-8") as f:
        f.write(line)


def get_today_logs() -> str:
    """Read today's log file."""
    path = _get_log_path()
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def get_logs_for_date(date_str: str) -> str:
    """Read logs for a specific date (YYYY-MM-DD)."""
    path = LOG_DIR / f"jarvis_{date_str}.log"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def get_available_log_dates() -> list[str]:
    """Get list of dates that have log files."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    dates = []
    for f in sorted(LOG_DIR.glob("jarvis_*.log")):
        date_part = f.stem.replace("jarvis_", "")
        dates.append(date_part)
    return dates


def cleanup_old_logs(days: int = 30):
    """Delete log files older than N days."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    cutoff = time.time() - (days * 86400)
    removed = 0
    for f in LOG_DIR.glob("jarvis_*.log"):
        if f.stat().st_mtime < cutoff:
            f.unlink()
            removed += 1
    return removed
