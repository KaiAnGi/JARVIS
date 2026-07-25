"""Jarvis Voice Assistant - CLI entry point."""

from core.config import load_env

load_env()

import threading
import time

from core.bootstrap import create_context


def main():
    bus, router, speaker, recognizer, wake_detector = create_context()
    bus.subscribe("speak", lambda text: speaker.speak(text))

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
