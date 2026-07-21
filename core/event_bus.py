"""Simple synchronous event bus for inter-component communication."""

from typing import Callable, Any


class EventBus:
    """Pub/sub event bus. Components emit events, others subscribe."""

    def __init__(self):
        self._subscribers: dict[str, list[Callable]] = {}

    def subscribe(self, event: str, callback: Callable):
        self._subscribers.setdefault(event, []).append(callback)

    def emit(self, event: str, data: Any = None):
        for callback in self._subscribers.get(event, []):
            callback(data)

    def unsubscribe(self, event: str, callback: Callable):
        if event in self._subscribers:
            self._subscribers[event] = [
                cb for cb in self._subscribers[event] if cb != callback
            ]
