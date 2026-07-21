"""Main Jarvis HUD window."""

from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPainter, QBrush, QPixmap
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QFrame,
    QGraphicsDropShadowEffect
)

from gui.styles import (
    PRIMARY_COLOR, SECONDARY_COLOR, BG_DARK, BG_PANEL,
    MAIN_STYLESHEET, PANEL_STYLE, BUTTON_STYLE, INPUT_STYLE, LOG_STYLE
)
from gui.widgets import ArcReactor, StatusIndicator


class VoiceThread(QThread):
    """Background thread for voice processing with session mode."""
    speech_detected = pyqtSignal(str)
    wake_detected = pyqtSignal(str)
    session_started = pyqtSignal()
    session_ended = pyqtSignal()

    GOODBYE_PHRASES = ["goodbye jarvis", "bye jarvis", "exit jarvis", "close jarvis",
                        "adiós jarvis", "adios jarvis", "hasta luego jarvis", "chao jarvis"]

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
            # STANDBY: listen for wake word
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

            # SESSION: listen for commands until goodbye
            while self._running and self._in_session:
                text = self.recognizer.listen_once()
                if not text:
                    continue
                lower = text.lower().strip()
                if any(phrase in lower for phrase in self.GOODBYE_PHRASES):
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

        self.setWindowTitle("J.A.R.V.I.S.")
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

        # Arc Reactor
        self.arc_reactor = ArcReactor(size=200)
        left_layout.addWidget(self.arc_reactor, alignment=Qt.AlignmentFlag.AlignCenter)

        # Status indicators
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

        # Version label
        version_label = QLabel("v1.0.0")
        version_label.setStyleSheet(f"color: {PRIMARY_COLOR}60; font-size: 11px;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(version_label)

        main_layout.addWidget(left_panel)

        # Right panel - Chat + Input
        right_panel = QFrame()
        right_panel.setStyleSheet(PANEL_STYLE)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(16, 16, 16, 16)

        # Header
        header = QLabel("J.A.R.V.I.S.")
        header.setFont(QFont("Consolas", 20, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {PRIMARY_COLOR}; background: transparent;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(header)

        subtitle = QLabel("Just A Rather Very Intelligent System")
        subtitle.setStyleSheet(f"color: {SECONDARY_COLOR}80; font-size: 11px; background: transparent;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(subtitle)

        # Log area
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet(LOG_STYLE)
        right_layout.addWidget(self.log_area, stretch=1)

        # Input area
        input_frame = QFrame()
        input_frame.setStyleSheet("background: transparent; border: none;")
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(0, 0, 0, 0)

        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Escribe un comando o di 'Hey Jarvis'...")
        self.text_input.setStyleSheet(INPUT_STYLE)
        self.text_input.returnPressed.connect(self._on_text_submit)
        input_layout.addWidget(self.text_input)

        self.send_btn = QPushButton("SEND")
        self.send_btn.setStyleSheet(BUTTON_STYLE)
        self.send_btn.setFixedWidth(100)
        self.send_btn.clicked.connect(self._on_text_submit)
        input_layout.addWidget(self.send_btn)

        right_layout.addWidget(input_frame)

        # Button bar
        btn_frame = QFrame()
        btn_frame.setStyleSheet("background: transparent; border: none;")
        btn_layout = QHBoxLayout(btn_frame)

        self.listen_btn = QPushButton("ACTIVATE")
        self.listen_btn.setStyleSheet(BUTTON_STYLE)
        self.listen_btn.clicked.connect(self._on_manual_listen)
        btn_layout.addWidget(self.listen_btn)

        self.clear_btn = QPushButton("CLEAR")
        self.clear_btn.setStyleSheet(BUTTON_STYLE)
        self.clear_btn.clicked.connect(lambda: self.log_area.clear())
        btn_layout.addWidget(self.clear_btn)

        right_layout.addWidget(btn_frame)

        main_layout.addWidget(right_panel, stretch=1)

    def _connect_signals(self):
        self.bus.subscribe("speak", lambda text: self._log("JARVIS", text))
        self.bus.subscribe("speak", lambda text: self.speaker.speak(text))

    def _log(self, sender: str, text: str):
        color = PRIMARY_COLOR if sender == "JARVIS" else SECONDARY_COLOR
        self.log_area.append(f'<span style="color:{color}">[{sender}]</span> {text}')

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
        self._log("SYSTEM", "Escuchando...")

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
        self.arc_reactor.set_listening(True)
        self.status_stt.set_active(True)
        self.status_wake.set_active(False)
        self._log("SYSTEM", "Sesión activa — habla tus comandos")
        self.speaker.speak("¿Sí?")

    def _on_session_end(self):
        self.arc_reactor.set_listening(False)
        self.status_stt.set_active(False)
        self.status_wake.set_active(True)
        self._log("SYSTEM", "Sesión terminada — di 'Hey Jarvis' para reactivar")
        self.speaker.speak("Adiós")

    def _on_wake(self, wake_word):
        pass

    def _on_speech(self, text):
        self._log("YOU", text)
        self.status_router.set_active(True)
        self.router.route(text, self.bus)
        QTimer.singleShot(500, lambda: self.status_router.set_active(False))

    def closeEvent(self, event):
        if self.voice_thread:
            self.voice_thread.stop()
        event.accept()
