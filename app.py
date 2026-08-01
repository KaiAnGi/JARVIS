"""Jarvis Desktop Application - GUI entry point."""

from core.config import load_env

load_env()

import sys
import threading

from PyQt6.QtNetwork import QLocalServer, QLocalSocket
from PyQt6.QtWidgets import QApplication

from core.bootstrap import create_context
from gui.main_window import JarvisWindow
from gui.tray import JarvisTray

SINGLE_INSTANCE_NAME = "jarvis.single.instance"


def main():
    ctx = create_context()

    # Qt App
    app = QApplication(sys.argv)
    app.setApplicationName("J.A.R.V.I.S.")

    # Single-instance guard: if Jarvis is already running, ask it to show its
    # window and exit instead of starting a duplicate copy.
    probe = QLocalSocket()
    probe.connectToServer(SINGLE_INSTANCE_NAME)
    if probe.waitForConnected(500):
        probe.write(b"show")
        probe.flush()
        probe.waitForBytesWritten(1000)
        sys.exit(0)

    server = QLocalServer()
    server.removeServer(SINGLE_INSTANCE_NAME)
    if not server.listen(SINGLE_INSTANCE_NAME):
        sys.exit(1)

    # Window — start hidden, appears on wake word
    window = JarvisWindow(ctx.recognizer, ctx.wake_detector, ctx.router, ctx.bus, ctx.speaker)
    window.showMinimized()
    window.hide()

    def on_show():
        window.showNormal()
        window.activateWindow()

    def on_new_connection():
        conn = server.nextPendingConnection()
        if conn is not None:
            conn.readAll()
            conn.disconnected.connect(conn.deleteLater)
            on_show()

    server.newConnection.connect(on_new_connection)

    # Start wake word in background
    window.start_voice_thread()

    # System tray (runs in separate thread)
    def on_quit():
        if window.voice_thread is not None:
            window.voice_thread.stop()
        window.close()
        app.quit()

    tray = JarvisTray(on_show, on_quit)

    tray_thread = threading.Thread(target=tray.start, daemon=True)
    tray_thread.start()

    # Cleanup on exit
    def cleanup():
        tray.stop()
        server.close()
        ctx.recognizer.cleanup()
        ctx.speaker.shutdown()

    app.aboutToQuit.connect(cleanup)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
