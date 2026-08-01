"""Main Jarvis HUD window."""

import time
import traceback

from PyQt6.QtCore import QObject, QRunnable, Qt, QThread, QThreadPool, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

import core.database as db
import core.logger as logger
from core.command_processor import route_with_fallback
from core.language import is_goodbye, resp, toggle_lang, ui
from gui.styles import (
    BUTTON_STYLE,
    INPUT_STYLE,
    LOG_STYLE,
    MAIN_STYLESHEET,
    PANEL_STYLE,
    PRIMARY_COLOR,
    SECONDARY_COLOR,
)
from gui.widgets import ArcReactor, StatusIndicator


class EventBridge(QObject):
    """Forwards bus events to the GUI thread via queued Qt signals.

    Plugins may emit events from worker threads; touching Qt widgets from
    those threads is unsafe, so events are marshalled here instead.
    """

    speak = pyqtSignal(str)
    language_changed = pyqtSignal(str)

    def __init__(self, bus):
        super().__init__()
        bus.subscribe("speak", self.speak.emit)
        bus.subscribe("language_changed", self.language_changed.emit)


class ListenThread(QThread):
    """Records a single utterance off the GUI thread."""

    finished_listening = pyqtSignal(str)

    def __init__(self, recognizer):
        super().__init__()
        self.recognizer = recognizer

    def run(self):
        text = self.recognizer.listen_once()
        self.finished_listening.emit(text)


class RouteTask(QRunnable):
    """Runs intent routing off the GUI thread so blocking plugin calls don't freeze the UI."""

    def __init__(self, router, bus, text, done_signal):
        super().__init__()
        self._router = router
        self._bus = bus
        self._text = text
        self._done_signal = done_signal

    def run(self):
        t0 = time.time()
        handled = False
        try:
            handled = route_with_fallback(self._text, self._router, self._bus)
        except Exception:
            logger.log_error("Router", traceback.format_exc())
            self._bus.emit("speak", resp("error"))
            handled = False
        finally:
            elapsed = (time.time() - t0) * 1000
            self._done_signal.emit(handled, self._text, elapsed)


class VoiceThread(QThread):
    """Background thread for voice processing with session mode."""

    speech_detected = pyqtSignal(str)
    wake_detected = pyqtSignal(str)
    session_started = pyqtSignal()
    session_ended = pyqtSignal()

    def __init__(self, recognizer, wake_detector, router, bus):
        super().__init__()
        self.recognizer = recognizer
        self.wake_detector = wake_detector
        self.router = router
        self.bus = bus
        self._running = True
        self._in_session = False

    def run(self):
        import time

        while self._running:
            self._in_session = False
            self.wake_detector.start_listening()
            while self._running and not self._in_session:
                wake_word = self.wake_detector.check()
                if wake_word:
                    self.wake_detector.stop_listening()
                    self._in_session = True
                    self.session_started.emit()
                    self.wake_detected.emit(wake_word)
                    break
                time.sleep(0.05)

            while self._running and self._in_session:
                text = self.recognizer.listen_once()
                if not text:
                    continue
                if is_goodbye(text):
                    self.session_ended.emit()
                    self._in_session = False
                    break
                self.speech_detected.emit(text)

            time.sleep(0.1)

    def stop(self):
        self._running = False
        self._in_session = False
        self.wake_detector.stop_listening()
        self.wait()


class JarvisWindow(QMainWindow):
    """Main HUD window styled like Iron Man's interface."""

    _routing_done = pyqtSignal(bool, str, float)

    def __init__(self, recognizer, wake_detector, router, bus, speaker):
        super().__init__()
        self.recognizer = recognizer
        self.wake_detector = wake_detector
        self.router = router
        self.bus = bus
        self.speaker = speaker
        self.voice_thread = None
        self._listen_thread = None
        self._session_id = 0
        self._session_active = False

        db.init()
        logger.log_event("SYSTEM", "J.A.R.V.I.S. started")

        self.setMinimumSize(900, 650)
        self.setStyleSheet(MAIN_STYLESHEET)

        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Left panel - Arc Reactor + Status
        left_panel = QFrame()
        left_panel.setStyleSheet(PANEL_STYLE)
        left_panel.setFixedWidth(280)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.arc_reactor = ArcReactor(size=200)
        left_layout.addWidget(self.arc_reactor, alignment=Qt.AlignmentFlag.AlignCenter)

        status_frame = QFrame()
        status_frame.setStyleSheet("background: transparent; border: none;")
        status_layout = QVBoxLayout(status_frame)
        status_layout.setContentsMargins(20, 10, 20, 10)

        self.status_wake = StatusIndicator("Wake Word", PRIMARY_COLOR)
        self.status_stt = StatusIndicator("Speech-to-Text", SECONDARY_COLOR)
        self.status_router = StatusIndicator("Intent Router", "#00FF88")
        self.status_tts = StatusIndicator("Text-to-Speech", "#FF4444")

        status_layout.addWidget(self.status_wake)
        status_layout.addWidget(self.status_stt)
        status_layout.addWidget(self.status_router)
        status_layout.addWidget(self.status_tts)

        left_layout.addWidget(status_frame)
        left_layout.addStretch()

        version_label = QLabel("v1.1.0")
        version_label.setStyleSheet(f"color: {PRIMARY_COLOR}60; font-size: 11px;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(version_label)

        main_layout.addWidget(left_panel)

        # Right panel - Chat + Input
        right_panel = QFrame()
        right_panel.setStyleSheet(PANEL_STYLE)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(16, 16, 16, 16)

        # Header row with language toggle
        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)

        self.header = QLabel(ui("header"))
        self.header.setFont(QFont("Consolas", 20, QFont.Weight.Bold))
        self.header.setStyleSheet(f"color: {PRIMARY_COLOR}; background: transparent;")
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_row.addWidget(self.header)

        self.lang_btn = QPushButton(ui("lang_btn"))
        self.lang_btn.setStyleSheet(
            f"QPushButton {{ background-color: {PRIMARY_COLOR}30; border: 1px solid {PRIMARY_COLOR}80; "
            f"border-radius: 12px; color: {PRIMARY_COLOR}; font-size: 12px; font-weight: bold; "
            f"padding: 4px 10px; min-width: 36px; }}"
            f"QPushButton:hover {{ background-color: {PRIMARY_COLOR}50; }}"
        )
        self.lang_btn.setFixedWidth(40)
        self.lang_btn.clicked.connect(self._toggle_language)
        header_row.addWidget(self.lang_btn, alignment=Qt.AlignmentFlag.AlignRight)

        right_layout.addLayout(header_row)

        self.subtitle = QLabel(ui("subtitle"))
        self.subtitle.setStyleSheet(f"color: {SECONDARY_COLOR}80; font-size: 11px; background: transparent;")
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(self.subtitle)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet(LOG_STYLE)
        right_layout.addWidget(self.log_area, stretch=1)

        input_frame = QFrame()
        input_frame.setStyleSheet("background: transparent; border: none;")
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(0, 0, 0, 0)

        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText(ui("placeholder"))
        self.text_input.setStyleSheet(INPUT_STYLE)
        self.text_input.returnPressed.connect(self._on_text_submit)
        input_layout.addWidget(self.text_input)

        self.send_btn = QPushButton(ui("send"))
        self.send_btn.setStyleSheet(BUTTON_STYLE)
        self.send_btn.setFixedWidth(100)
        self.send_btn.clicked.connect(self._on_text_submit)
        input_layout.addWidget(self.send_btn)

        right_layout.addWidget(input_frame)

        btn_frame = QFrame()
        btn_frame.setStyleSheet("background: transparent; border: none;")
        btn_layout = QHBoxLayout(btn_frame)

        self.listen_btn = QPushButton(ui("activate"))
        self.listen_btn.setStyleSheet(BUTTON_STYLE)
        self.listen_btn.clicked.connect(self._on_manual_listen)
        btn_layout.addWidget(self.listen_btn)

        self.clear_btn = QPushButton(ui("clear"))
        self.clear_btn.setStyleSheet(BUTTON_STYLE)
        self.clear_btn.clicked.connect(lambda: self.log_area.clear())
        btn_layout.addWidget(self.clear_btn)

        right_layout.addWidget(btn_frame)

        main_layout.addWidget(right_panel, stretch=1)

    def _connect_signals(self):
        self.bus.subscribe("speak", lambda text: self.speaker.speak(text))
        self._bridge = EventBridge(self.bus)
        self._bridge.speak.connect(self._on_speak_event)
        self._bridge.language_changed.connect(self._on_language_changed)
        self._routing_done.connect(self._on_routing_done)

    def _on_speak_event(self, text):
        self._log("JARVIS", text)

    def _on_language_changed(self, lang):
        self._apply_language_change(lang)

    def _apply_language_change(self, lang: str):
        self.recognizer.switch_language()
        self.speaker.switch_language()
        self.router.rebuild_patterns()
        self._refresh_ui()
        label = "Idioma: Español" if lang == "es" else "Language: English"
        self._log("SYSTEM", label)

    def _log(self, sender: str, text: str):
        color = PRIMARY_COLOR if sender == "JARVIS" else SECONDARY_COLOR
        self.log_area.append(f'<span style="color:{color}">[{sender}]</span> {text}')
        if sender in ("YOU", "JARVIS"):
            db.save_conversation(sender, text, self._session_id)
        logger.log_event(sender, text)

    def _toggle_language(self):
        self._apply_language_change(toggle_lang())

    def _refresh_ui(self):
        self.setWindowTitle(ui("window_title"))
        self.header.setText(ui("header"))
        self.subtitle.setText(ui("subtitle"))
        self.text_input.setPlaceholderText(ui("placeholder"))
        self.send_btn.setText(ui("send"))
        self.listen_btn.setText(ui("activate"))
        self.clear_btn.setText(ui("clear"))
        self.lang_btn.setText(ui("lang_btn"))

    def _route_async(self, text: str):
        """Route a command on a worker thread so blocking plugins don't freeze the UI."""
        self.status_router.set_active(True)
        pool = QThreadPool.globalInstance()
        if pool is not None:
            pool.start(RouteTask(self.router, self.bus, text, self._routing_done))

    def _on_routing_done(self, handled: bool, text: str, elapsed: float):
        action = text.split()[0] if text else "voice"
        db.save_command(action, text, success=handled, duration_ms=elapsed)
        QTimer.singleShot(500, lambda: self.status_router.set_active(False))

    def _on_text_submit(self):
        text = self.text_input.text().strip()
        if not text:
            return
        self.text_input.clear()
        self._log("YOU", text)
        self._route_async(text)

    def _on_manual_listen(self):
        if self._listen_thread is not None and self._listen_thread.isRunning():
            return
        if self._session_active:
            return
        self.arc_reactor.set_listening(True)
        self.status_stt.set_active(True)
        self._log("SYSTEM", ui("listening"))

        self._listen_thread = ListenThread(self.recognizer)
        self._listen_thread.finished_listening.connect(self._on_listen_finished_text)
        self._listen_thread.finished.connect(self._on_listen_finished)
        self._listen_thread.start()

    def _on_listen_finished_text(self, text: str):
        if text:
            self._log("YOU", text)
            self._route_async(text)
        self.arc_reactor.set_listening(False)
        self.status_stt.set_active(False)

    def _on_listen_finished(self):
        self._listen_thread = None

    def start_voice_thread(self):
        self.voice_thread = VoiceThread(self.recognizer, self.wake_detector, self.router, self.bus)
        self.voice_thread.wake_detected.connect(self._on_wake)
        self.voice_thread.speech_detected.connect(self._on_speech)
        self.voice_thread.session_started.connect(self._on_session_start)
        self.voice_thread.session_ended.connect(self._on_session_end)
        self.voice_thread.start()
        self.status_wake.set_active(True)

    def _on_session_start(self):
        self._session_active = True
        self._session_id = int(time.time())
        logger.log_session_start()
        self.showNormal()
        self.activateWindow()
        self.raise_()
        self.arc_reactor.set_listening(True)
        self.status_stt.set_active(True)
        self.status_wake.set_active(False)
        self._log("SYSTEM", ui("session_active"))
        self.speaker.speak(ui("yes"))
        browser = self.router.get_plugin("browser")
        if browser is not None and hasattr(browser, "reset_state"):
            browser.reset_state()

    def _on_session_end(self):
        self._session_active = False
        self.arc_reactor.set_listening(False)
        self.status_stt.set_active(False)
        self.status_wake.set_active(True)
        self._log("SYSTEM", ui("session_ended"))
        logger.log_session_end()
        self.speaker.speak(ui("goodbye"))
        QTimer.singleShot(1500, self.hide)

    def _on_wake(self, wake_word):
        pass

    def _on_speech(self, text):
        self._log("YOU", text)
        self._route_async(text)

    def closeEvent(self, event):
        logger.log_event("SYSTEM", "J.A.R.V.I.S. shutting down")
        if self._listen_thread is not None and self._listen_thread.isRunning():
            self._listen_thread.quit()
            self._listen_thread.wait(2000)
        event.ignore()
        self.hide()
