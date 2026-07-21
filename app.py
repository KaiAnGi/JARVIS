"""Jarvis Desktop Application - Entry point."""

import sys
import threading

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from core.event_bus import EventBus
from core.audio_input import SpeechRecognizer
from core.audio_output import Speaker
from core.intent_router import IntentRouter
from core.plugin_loader import load_plugins
from core.wake_word import WakeWordDetector

from gui.main_window import FloatingJarvis
from gui.tray import JarvisTray


def main():
    bus = EventBus()
    router = IntentRouter()
    speaker = Speaker()
    recognizer = SpeechRecognizer()
    wake_detector = WakeWordDetector(wake_words=["hey_jarvis_v0.1"], threshold=0.5)

    load_plugins(bus, router)

    app = QApplication(sys.argv)
    app.setApplicationName("J.A.R.V.I.S.")
    app.setQuitOnLastWindowClosed(False)

    window = FloatingJarvis(recognizer, wake_detector, router, bus, speaker)
    window.start_voice_thread()

    def on_show():
        window.show_with_animation()

    def on_quit():
        window.hide()
        app.quit()

    tray = JarvisTray(on_show, on_quit)
    tray_thread = threading.Thread(target=tray.start, daemon=True)
    tray_thread.start()

    def cleanup():
        tray.stop()
        recognizer.cleanup()
        speaker.shutdown()

    app.aboutToQuit.connect(cleanup)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
