"""Persistent text logging to daily log files using stdlib logging."""

import logging
import time
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent / "data" / "logs"

_logger = None


def _get_logger() -> logging.Logger:
    """Get or create the module-level logger with daily rotation."""
    global _logger
    if _logger is not None:
        return _logger

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    _logger = logging.getLogger("jarvis")
    _logger.setLevel(logging.DEBUG)
    _logger.propagate = False

    if not _logger.handlers:
        handler = TimedRotatingFileHandler(
            LOG_DIR / "jarvis.log",
            when="midnight",
            backupCount=30,
            encoding="utf-8",
        )
        handler.setFormatter(logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%H:%M:%S",
        ))
        _logger.addHandler(handler)

    return _logger


def log_event(sender: str, text: str, event_type: str = "INFO"):
    """Log an event to today's log file."""
    logger = _get_logger()
    level = getattr(logging, event_type.upper(), logging.INFO)
    logger.log(level, "[%s] %s", sender, text)


def log_command(action: str, parameters: str = "", success: bool = True, duration_ms: float = 0):
    """Log a command execution."""
    logger = _get_logger()
    status = "OK" if success else "FAIL"
    msg = f"[CMD] [{status}] {action}"
    if parameters:
        msg += f" | {parameters}"
    if duration_ms:
        msg += f" | {duration_ms:.0f}ms"
    logger.info(msg)


def log_error(component: str, error: str):
    """Log an error."""
    logger = _get_logger()
    logger.error("[%s] %s", component, error)


def log_session_start():
    """Log session start."""
    logger = _get_logger()
    logger.info("[SESSION] === Session started ===")


def log_session_end():
    """Log session end."""
    logger = _get_logger()
    logger.info("[SESSION] === Session ended ===")


def get_today_logs() -> str:
    """Read today's log file."""
    today = datetime.now().strftime("%Y-%m-%d")
    path = LOG_DIR / f"jarvis.log"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def get_logs_for_date(date_str: str) -> str:
    """Read logs for a specific date (YYYY-MM-DD)."""
    path = LOG_DIR / f"jarvis.log.{date_str}"
    if path.exists():
        return path.read_text(encoding="utf-8")
    # Today's logs are in the active file
    if date_str == datetime.now().strftime("%Y-%m-%d"):
        return get_today_logs()
    return ""


def get_available_log_dates() -> list[str]:
    """Get list of dates that have log files."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    dates = []
    for f in sorted(LOG_DIR.glob("jarvis.log*")):
        name = f.name
        if "." in name:
            date_part = name.split(".", 1)[1]
            if date_part and date_part[0].isdigit():
                dates.append(date_part)
    return dates


def cleanup_old_logs(days: int = 30):
    """Delete log files older than N days. Handled automatically by TimedRotatingFileHandler."""
    pass
