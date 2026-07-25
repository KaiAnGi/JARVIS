"""Shared test fixtures."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def bus():
    """Mock EventBus that captures emitted events.

    Each new test gets a fresh mock. ``emit`` calls are recorded into
    ``bus._events`` as ``(event_name, data)`` tuples.  The captured
    list is cleared automatically when the fixture resets its mock
    (i.e. between tests) so there is no leakage.
    """
    mock = MagicMock()
    mock._events = []

    def capture(event, data=None):
        mock._events.append((event, data))

    mock.emit.side_effect = capture
    yield mock
    mock._events.clear()


@pytest.fixture(autouse=True)
def reset_language():
    """Reset language to Spanish before each test."""
    from core.language import set_lang
    set_lang("es")
    yield
    set_lang("es")


@pytest.fixture
def tmp_db(tmp_path, monkeypatch):
    """Redirect database to a temporary path."""
    import core.database as db
    monkeypatch.setattr(db, "DB_DIR", tmp_path)
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    db.init()
    return db


@pytest.fixture
def tmp_favorites(tmp_path, monkeypatch):
    """Redirect favorites to a temporary path."""
    import core.favorites as fav
    fav_path = tmp_path / "favorites.json"
    monkeypatch.setattr(fav, "FAVORITES_PATH", fav_path)
    return fav
