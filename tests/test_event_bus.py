"""Tests for core/event_bus.py"""

from core.event_bus import EventBus


class TestEventBus:
    def test_subscribe_and_emit(self):
        bus = EventBus()
        received = []
        bus.subscribe("test", lambda data: received.append(data))
        bus.emit("test", "hello")
        assert received == ["hello"]

    def test_multiple_subscribers(self):
        bus = EventBus()
        results = []
        bus.subscribe("test", lambda d: results.append("a"))
        bus.subscribe("test", lambda d: results.append("b"))
        bus.emit("test")
        assert results == ["a", "b"]

    def test_emit_no_subscribers(self):
        bus = EventBus()
        bus.emit("nonexistent", "data")  # Should not raise

    def test_unsubscribe(self):
        bus = EventBus()
        received = []

        def callback(data):
            received.append(data)

        bus.subscribe("test", callback)
        bus.unsubscribe("test", callback)
        bus.emit("test", "hello")
        assert received == []

    def test_unsubscribe_nonexistent_event(self):
        bus = EventBus()
        bus.unsubscribe("nonexistent", lambda d: None)  # Should not raise

    def test_multiple_events(self):
        bus = EventBus()
        results = {}
        bus.subscribe("a", lambda d: results.__setitem__("a", d))
        bus.subscribe("b", lambda d: results.__setitem__("b", d))
        bus.emit("a", 1)
        bus.emit("b", 2)
        assert results == {"a": 1, "b": 2}

    def test_emit_with_none_data(self):
        bus = EventBus()
        received = []
        bus.subscribe("test", lambda d: received.append(d))
        bus.emit("test")
        assert received == [None]

    def test_subscriber_exception_does_not_break_others(self):
        bus = EventBus()
        results = []
        bus.subscribe("test", lambda d: 1 / 0)
        bus.subscribe("test", lambda d: results.append("ok"))
        bus.emit("test")
        assert results == ["ok"]
