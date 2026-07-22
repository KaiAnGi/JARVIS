"""JSON-based favorites system for frequently used commands."""

import json
from pathlib import Path

FAVORITES_PATH = Path(__file__).resolve().parent.parent / "data" / "favorites.json"

DEFAULT_FAVORITES = {
    "apps": {},
    "searches": {},
    "commands": {},
}


def _load() -> dict:
    """Load favorites from JSON file."""
    if FAVORITES_PATH.exists():
        try:
            return json.loads(FAVORITES_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return DEFAULT_FAVORITES.copy()


def _save(data: dict):
    """Save favorites to JSON file."""
    FAVORITES_PATH.parent.mkdir(parents=True, exist_ok=True)
    FAVORITES_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def add_app(name: str, path: str):
    """Add a favorite app."""
    data = _load()
    data["apps"][name.lower()] = {"path": path, "uses": data["apps"].get(name.lower(), {}).get("uses", 0)}
    _save(data)


def add_search(query: str):
    """Add a favorite search query."""
    data = _load()
    key = query.lower().strip()
    entry = data["searches"].get(key, {"uses": 0})
    entry["uses"] = entry.get("uses", 0) + 1
    data["searches"][key] = entry
    _save(data)


def add_command(action: str, text: str):
    """Add a favorite command (a voice phrase the user frequently uses)."""
    data = _load()
    key = text.lower().strip()
    entry = data["commands"].get(key, {"action": action, "uses": 0})
    entry["uses"] = entry.get("uses", 0) + 1
    data["commands"][key] = entry
    _save(data)


def get_apps() -> dict:
    """Get all favorite apps."""
    return _load().get("apps", {})


def get_searches() -> dict:
    """Get all favorite searches."""
    return _load().get("searches", {})


def get_commands() -> dict:
    """Get all favorite commands."""
    return _load().get("commands", {})


def get_top_commands(limit: int = 5) -> list[dict]:
    """Get most used favorite commands."""
    commands = get_commands()
    sorted_cmds = sorted(commands.items(), key=lambda x: x[1].get("uses", 0), reverse=True)
    return [{"text": k, "action": v["action"], "uses": v.get("uses", 0)} for k, v in sorted_cmds[:limit]]


def get_top_searches(limit: int = 5) -> list[dict]:
    """Get most used favorite searches."""
    searches = get_searches()
    sorted_s = sorted(searches.items(), key=lambda x: x[1].get("uses", 0), reverse=True)
    return [{"query": k, "uses": v.get("uses", 0)} for k, v in sorted_s[:limit]]


def remove(category: str, key: str) -> bool:
    """Remove a favorite by category (apps/searches/commands) and key."""
    data = _load()
    if category in data and key.lower() in data[category]:
        del data[category][key.lower()]
        _save(data)
        return True
    return False


def search(query: str) -> list[dict]:
    """Search favorites matching a query string."""
    data = _load()
    results = []
    q = query.lower()
    for key, val in data.get("commands", {}).items():
        if q in key:
            results.append({"type": "command", "text": key, "action": val["action"]})
    for key, val in data.get("apps", {}).items():
        if q in key:
            results.append({"type": "app", "name": key, "path": val["path"]})
    for key, val in data.get("searches", {}).items():
        if q in key:
            results.append({"type": "search", "query": key})
    return results
