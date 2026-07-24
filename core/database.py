"""SQLite database for conversation memory and command history."""

import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DB_DIR / "jarvis.db"


@contextmanager
def _connect():
    """Context manager for SQLite connections with WAL mode."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init():
    """Create tables if they don't exist."""
    with _connect() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                session_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                text TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                action TEXT NOT NULL,
                parameters TEXT,
                success INTEGER DEFAULT 1,
                duration_ms REAL
            );

            CREATE INDEX IF NOT EXISTS idx_conv_session ON conversations(session_id);
            CREATE INDEX IF NOT EXISTS idx_conv_ts ON conversations(timestamp);
            CREATE INDEX IF NOT EXISTS idx_cmd_ts ON commands(timestamp);
            CREATE INDEX IF NOT EXISTS idx_cmd_action ON commands(action);
        """)


# ── Conversations ──────────────────────────────────────────────────

def save_conversation(role: str, text: str, session_id: int):
    """Save a conversation turn (user or jarvis)."""
    with _connect() as conn:
        conn.execute(
            "INSERT INTO conversations (timestamp, session_id, role, text) VALUES (?, ?, ?, ?)",
            (time.time(), session_id, role, text),
        )


def get_recent_conversations(limit: int = 20, session_id: int = None) -> list[dict]:
    """Get recent conversation turns, optionally filtered by session."""
    with _connect() as conn:
        if session_id is not None:
            rows = conn.execute(
                "SELECT timestamp, role, text FROM conversations WHERE session_id = ? ORDER BY id DESC LIMIT ?",
                (session_id, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT timestamp, role, text FROM conversations ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
    return [{"timestamp": r[0], "role": r[1], "text": r[2]} for r in reversed(rows)]


def get_conversation_context(session_id: int, limit: int = 10) -> str:
    """Get recent conversation as a string for LLM context."""
    turns = get_recent_conversations(limit=limit, session_id=session_id)
    lines = []
    for t in turns:
        prefix = "User" if t["role"] == "YOU" else "JARVIS"
        lines.append(f"{prefix}: {t['text']}")
    return "\n".join(lines)


# ── Commands ───────────────────────────────────────────────────────

def save_command(action: str, parameters: str = "", success: bool = True, duration_ms: float = 0):
    """Log a executed command."""
    with _connect() as conn:
        conn.execute(
            "INSERT INTO commands (timestamp, action, parameters, success, duration_ms) VALUES (?, ?, ?, ?, ?)",
            (time.time(), action, parameters, int(success), duration_ms),
        )


def get_command_history(limit: int = 50, action: str = None) -> list[dict]:
    """Get command history, optionally filtered by action type."""
    with _connect() as conn:
        if action:
            rows = conn.execute(
                "SELECT timestamp, action, parameters, success, duration_ms FROM commands WHERE action = ? ORDER BY id DESC LIMIT ?",
                (action, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT timestamp, action, parameters, success, duration_ms FROM commands ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
    return [
        {"timestamp": r[0], "action": r[1], "parameters": r[2], "success": bool(r[3]), "duration_ms": r[4]}
        for r in rows
    ]


def get_frequent_commands(limit: int = 10) -> list[dict]:
    """Get most frequently used commands."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT action, COUNT(*) as count FROM commands GROUP BY action ORDER BY count DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [{"action": r[0], "count": r[1]} for r in rows]


def get_stats() -> dict:
    """Get usage statistics."""
    with _connect() as conn:
        total = conn.execute("SELECT COUNT(*) FROM commands").fetchone()[0]
        success = conn.execute("SELECT COUNT(*) FROM commands WHERE success = 1").fetchone()[0]
        sessions = conn.execute("SELECT COUNT(DISTINCT session_id) FROM conversations").fetchone()[0]
        first = conn.execute("SELECT MIN(timestamp) FROM commands").fetchone()[0]
    return {
        "total_commands": total,
        "successful": success,
        "success_rate": f"{(success/total*100):.1f}%" if total else "0%",
        "total_sessions": sessions,
        "first_used": first,
    }
