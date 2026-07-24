"""Jarvis Voice Assistant - Entry point."""

from core.config import load_env
load_env()

import threading
import time

from core.event_bus import EventBus
from core.audio_input import SpeechRecognizer
from core.audio_output import Speaker
from core.intent_router import IntentRouter
from core.plugin_loader import load_plugins
from core.wake_word import WakeWordDetector


def main():
    bus = EventBus()
    router = IntentRouter()

    speaker = Speaker()
    bus.subscribe("speak", lambda text: speaker.speak(text))

    load_plugins(bus, router)

    recognizer = SpeechRecognizer()
    wake_detector = WakeWordDetector(wake_words=["hey_jarvis"], threshold=0.5)

    stop = threading.Event()

    def on_speech(text):
        print(f"You: {text}")
        if not router.route(text, bus):
            print("(no matching command)")

    print("Loading wake word model...")
    wake_detector.load()

    print("Jarvis ready. Say 'Hey Jarvis' to activate (Ctrl+C to quit).")
    try:
        while not stop.is_set():
            wake_detector.start_listening()
            while not stop.is_set():
                wake_word = wake_detector.check()
                if wake_word:
                    wake_detector.stop_listening()
                    print(f"[WAKE] Detected: {wake_word}")
                    speaker.speak("Yes?")
                    time.sleep(0.5)
                    text = recognizer.listen_once()
                    if text:
                        on_speech(text)
                    break
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        stop.set()
    finally:
        wake_detector.stop_listening()
        recognizer.cleanup()
        speaker.shutdown()


if __name__ == "__main__":
    main()
