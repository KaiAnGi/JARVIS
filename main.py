"""Jarvis Voice Assistant - Entry point."""

import threading

from core.event_bus import EventBus
from core.audio_input import SpeechRecognizer
from core.audio_output import Speaker
from core.intent_router import IntentRouter
from core.plugin_loader import load_plugins


def main():
    bus = EventBus()
    router = IntentRouter()

    speaker = Speaker()
    bus.subscribe("speak", lambda text: speaker.speak(text))

    load_plugins(bus, router)

    recognizer = SpeechRecognizer()

    stop = threading.Event()

    def on_speech(text):
        print(f"You: {text}")
        if not router.route(text, bus):
            print("(no matching command)")

    print("Jarvis ready. Say something (Ctrl+C to quit).")
    try:
        recognizer.listen_continuous(on_speech, stop_event=stop)
    except KeyboardInterrupt:
        print("\nShutting down...")
        stop.set()
    finally:
        recognizer.cleanup()
        speaker.shutdown()


if __name__ == "__main__":
    main()
