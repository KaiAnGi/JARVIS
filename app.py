"""Jarvis Desktop Application - GUI entry point."""

from core.config import load_env

load_env()

import sys
import threading

from PyQt6.QtWidgets import QApplication

from core.bootstrap import create_context
from gui.main_window import JarvisWindow
from gui.tray import JarvisTray


def main():
    bus, router, speaker, recognizer, wake_detector = create_context()

    # Qt App
    app = QApplication(sys.argv)
    app.setApplicationName("J.A.R.V.I.S.")

    # Window — start hidden, appears on wake word
    window = JarvisWindow(recognizer, wake_detector, router, bus, speaker)
    window.showMinimized()
    window.hide()

    # Start wake word in background
    window.start_voice_thread()

    # System tray (runs in separate thread)
    def on_show():
        window.showNormal()
        window.activateWindow()

    def on_quit():
        window.voice_thread.stop()
        window.close()
        app.quit()

    tray = JarvisTray(on_show, on_quit)

    tray_thread = threading.Thread(target=tray.start, daemon=True)
    tray_thread.start()

    # Cleanup on exit
    def cleanup():
        tray.stop()
        recognizer.cleanup()
        speaker.shutdown()

    app.aboutToQuit.connect(cleanup)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
