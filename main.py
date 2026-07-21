"""Jarvis Voice Assistant - Entry point."""

from core.event_bus import EventBus


def main():
    bus = EventBus()
    print("Jarvis Assistant starting...")
    print("Core initialized. Ready for step 2 (audio).")


if __name__ == "__main__":
    main()
