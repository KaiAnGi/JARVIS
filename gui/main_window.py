"""Main Jarvis HUD window."""

from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QFrame,
)

from gui.styles import (
    PRIMARY_COLOR, SECONDARY_COLOR, BG_DARK, BG_PANEL,
    MAIN_STYLESHEET, PANEL_STYLE, BUTTON_STYLE, INPUT_STYLE, LOG_STYLE
)
from gui.widgets import ArcReactor, StatusIndicator
from core.language import ui, toggle_lang, is_goodbye, set_lang


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

    def __init__(self, recognizer, wake_detector, router, bus, speaker):
        super().__init__()
        self.recognizer = recognizer
        self.wake_detector = wake_detector
        self.router = router
        self.bus = bus
        self.speaker = speaker
        self.voice_thread = None

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
        self.bus.subscribe("speak", lambda text: self._log("JARVIS", text))
        self.bus.subscribe("speak", lambda text: self.speaker.speak(text))
        self.bus.subscribe("language_changed", lambda lang: self._on_language_changed(lang))

    def _on_language_changed(self, lang):
        self.recognizer.switch_language()
        self.speaker.switch_language()
        self.router.rebuild_patterns()
        self._refresh_ui()
        self._log("SYSTEM", f"{'Idioma: Español' if lang == 'es' else 'Language: English'}")

    def _log(self, sender: str, text: str):
        color = PRIMARY_COLOR if sender == "JARVIS" else SECONDARY_COLOR
        self.log_area.append(f'<span style="color:{color}">[{sender}]</span> {text}')

    def _toggle_language(self):
        new_lang = toggle_lang()
        self.recognizer.switch_language()
        self.speaker.switch_language()
        self.router.rebuild_patterns()
        self._refresh_ui()
        self._log("SYSTEM", f"{'Idioma: Español' if new_lang == 'es' else 'Language: English'}")

    def _refresh_ui(self):
        self.setWindowTitle(ui("window_title"))
        self.header.setText(ui("header"))
        self.subtitle.setText(ui("subtitle"))
        self.text_input.setPlaceholderText(ui("placeholder"))
        self.send_btn.setText(ui("send"))
        self.listen_btn.setText(ui("activate"))
        self.clear_btn.setText(ui("clear"))
        self.lang_btn.setText(ui("lang_btn"))

    def _on_text_submit(self):
        text = self.text_input.text().strip()
        if not text:
            return
        self.text_input.clear()
        self._log("YOU", text)
        self.status_router.set_active(True)
        self.router.route(text, self.bus)
        QTimer.singleShot(500, lambda: self.status_router.set_active(False))

    def _on_manual_listen(self):
        self.arc_reactor.set_listening(True)
        self.status_stt.set_active(True)
        self._log("SYSTEM", ui("listening"))

        def listen_in_thread():
            text = self.recognizer.listen_once()
            if text:
                self._log("YOU", text)
                self.router.route(text, self.bus)
            self.arc_reactor.set_listening(False)
            self.status_stt.set_active(False)

        thread = QThread(target=listen_in_thread)
        thread.start()

    def start_voice_thread(self):
        self.voice_thread = VoiceThread(
            self.recognizer, self.wake_detector, self.router, self.bus
        )
        self.voice_thread.wake_detected.connect(self._on_wake)
        self.voice_thread.speech_detected.connect(self._on_speech)
        self.voice_thread.session_started.connect(self._on_session_start)
        self.voice_thread.session_ended.connect(self._on_session_end)
        self.voice_thread.start()
        self.status_wake.set_active(True)

    def _on_session_start(self):
        self.showNormal()
        self.activateWindow()
        self.raise_()
        self.arc_reactor.set_listening(True)
        self.status_stt.set_active(True)
        self.status_wake.set_active(False)
        self._log("SYSTEM", ui("session_active"))
        self.speaker.speak(ui("yes"))

    def _on_session_end(self):
        self.arc_reactor.set_listening(False)
        self.status_stt.set_active(False)
        self.status_wake.set_active(True)
        self._log("SYSTEM", ui("session_ended"))
        self.speaker.speak(ui("goodbye"))
        QTimer.singleShot(1500, self.hide)

    def _on_wake(self, wake_word):
        pass

    def _on_speech(self, text):
        self._log("YOU", text)
        self.status_router.set_active(True)
        handled = self.router.route(text, self.bus)
        if not handled:
            browser = self.router._plugins.get("browser")
            if browser and hasattr(browser, "_waiting_youtube") and browser._waiting_youtube:
                browser.handle("youtube_search", text, self.bus)
            else:
                from core.language import resp
                self.bus.emit("speak", resp("no_match"))
        QTimer.singleShot(500, lambda: self.status_router.set_active(False))

    def closeEvent(self, event):
        event.ignore()
        self.hide()
