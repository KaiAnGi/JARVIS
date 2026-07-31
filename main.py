"""Jarvis Voice Assistant - CLI entry point."""

from core.config import load_env

load_env()

import threading
import time

from core.bootstrap import create_context


def main():
    ctx = create_context()
    ctx.bus.subscribe("speak", lambda text: ctx.speaker.speak(text))

    stop = threading.Event()

    def on_speech(text):
        print(f"You: {text}")
        if ctx.router.route(text, ctx.bus):
            return

        browser = ctx.router.get_plugin("browser")
        if browser is not None and getattr(browser, "is_waiting_youtube", None) and browser.is_waiting_youtube():
            browser.handle("youtube_search", text, ctx.bus)
            return

        from core.command_processor import process_unmatched
        from core.language import resp

        ctx.bus.emit("speak", resp("processing"))
        process_unmatched(text, ctx.router, ctx.bus)

    print("Loading wake word model...")
    ctx.wake_detector.load()

    print("Jarvis ready. Say 'Hey Jarvis' to activate (Ctrl+C to quit).")
    try:
        while not stop.is_set():
            ctx.wake_detector.start_listening()
            while not stop.is_set():
                wake_word = ctx.wake_detector.check()
                if wake_word:
                    ctx.wake_detector.stop_listening()
                    print(f"[WAKE] Detected: {wake_word}")
                    ctx.speaker.speak("Yes?")
                    time.sleep(0.5)
                    text = ctx.recognizer.listen_once()
                    if text:
                        on_speech(text)
                    break
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        stop.set()
    finally:
        ctx.wake_detector.stop_listening()
        ctx.recognizer.cleanup()
        ctx.speaker.shutdown()


if __name__ == "__main__":
    main()
