"""Floating Spotlight-style Jarvis interface."""

from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QColor, QPainter, QPainterPath, QBrush, QPen, QKeyEvent
from PyQt6.QtWidgets import (
    QWidget, QLineEdit, QTextEdit, QLabel, QHBoxLayout,
    QVBoxLayout, QGraphicsDropShadowEffect, QApplication
)

from gui.styles import PRIMARY_COLOR, SECONDARY_COLOR, BG_DARK, BG_PANEL
from gui.widgets import ArcReactor
from core.language import ui, toggle_lang, is_goodbye, get_lang


class VoiceThread(QThread):
    speech_detected = pyqtSignal(str)
    wake_detected = pyqtSignal(str)
    session_started = pyqtSignal()
    session_ended = pyqtSignal()

    def __init__(self, recognizer, wake_detector):
        super().__init__()
        self.recognizer = recognizer
        self.wake_detector = wake_detector
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


class FloatingJarvis(QWidget):
    """Spotlight-style floating search bar."""

    WIDTH = 620
    HEIGHT_COLLAPSED = 60
    HEIGHT_EXPANDED = 380

    def __init__(self, recognizer, wake_detector, router, bus, speaker):
        super().__init__()
        self.recognizer = recognizer
        self.wake_detector = wake_detector
        self.router = router
        self.bus = bus
        self.speaker = speaker
        self.voice_thread = None
        self._expanded = False

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        Qt.WindowType.WindowTransparentForInput
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)

        self.setFixedWidth(self.WIDTH)
        self.setFixedHeight(self.HEIGHT_COLLAPSED)

        self._center_on_screen()
        self._init_ui()
        self._connect_signals()
        self._init_animations()

    def _center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.WIDTH) // 2
        y = int(screen.height() * 0.25)
        self.move(x, y)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Main container
        self.container = QWidget()
        self.container.setObjectName("container")
        self.container.setStyleSheet(f"""
            #container {{
                background-color: rgba(12, 12, 20, 230);
                border: 1px solid {PRIMARY_COLOR}40;
                border-radius: 16px;
            }}
        """)
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(16, 12, 16, 12)
        container_layout.setSpacing(8)

        # Top row: input + lang button
        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        # Arc reactor (small)
        self.arc_reactor = ArcReactor(size=36)
        self.arc_reactor.setFixedSize(36, 36)
        top_row.addWidget(self.arc_reactor)

        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText(ui("placeholder"))
        self.text_input.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                border: none;
                color: #E0E0E0;
                font-size: 16px;
                font-family: 'Segoe UI', sans-serif;
                padding: 4px 0;
            }}
            QLineEdit::placeholder {{
                color: #666666;
            }}
        """)
        self.text_input.returnPressed.connect(self._on_submit)
        top_row.addWidget(self.text_input, stretch=1)

        self.lang_btn = QLabel(ui("lang_btn"))
        self.lang_btn.setFixedSize(32, 32)
        self.lang_btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lang_btn.setStyleSheet(f"""
            QLabel {{
                color: {PRIMARY_COLOR};
                font-size: 11px;
                font-weight: bold;
                border: 1px solid {PRIMARY_COLOR}60;
                border-radius: 10px;
                background: {PRIMARY_COLOR}15;
            }}
            QLabel:hover {{
                background: {PRIMARY_COLOR}30;
            }}
        """)
        self.lang_btn.mousePressEvent = lambda _: self._toggle_language()
        top_row.addWidget(self.lang_btn)

        container_layout.addLayout(top_row)

        # Log area (hidden initially)
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet(f"""
            QTextEdit {{
                background: transparent;
                border: none;
                color: {SECONDARY_COLOR};
                font-family: 'Consolas', monospace;
                font-size: 12px;
                padding: 4px 0;
            }}
            QScrollBar:vertical {{
                width: 4px;
                background: transparent;
            }}
            QScrollBar::handle:vertical {{
                background: {PRIMARY_COLOR}30;
                border-radius: 2px;
                min-height: 20px;
            }}
        """)
        self.log_area.setVisible(False)
        container_layout.addWidget(self.log_area, stretch=1)

        layout.addWidget(self.container)

        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(PRIMARY_COLOR + "60"))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)

    def _connect_signals(self):
        self.bus.subscribe("speak", lambda text: self._log("JARVIS", text))
        self.bus.subscribe("speak", lambda text: self.speaker.speak(text))

    def _init_animations(self):
        self._show_anim = QPropertyAnimation(self, b"geometry")
        self._show_anim.setDuration(200)
        self._show_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._hide_anim = QPropertyAnimation(self, b"geometry")
        self._hide_anim.setDuration(180)
        self._hide_anim.setEasingCurve(QEasingCurve.Type.InCubic)
        self._hide_anim.finished.connect(self.hide)

    def _log(self, sender: str, text: str):
        color = PRIMARY_COLOR if sender == "JARVIS" else SECONDARY_COLOR
        self.log_area.append(f'<span style="color:{color}">[{sender}]</span> {text}')

    def _on_submit(self):
        text = self.text_input.text().strip()
        if not text:
            return
        self.text_input.clear()
        self._log("YOU", text)
        self.router.route(text, self.bus)

    def _toggle_language(self):
        new_lang = toggle_lang()
        self.recognizer.switch_language()
        self.speaker.switch_language()
        self.router.rebuild_patterns()
        self.text_input.setPlaceholderText(ui("placeholder"))
        self.lang_btn.setText(ui("lang_btn"))
        self._log("SYSTEM", f"{'Idioma: Español' if new_lang == 'es' else 'Language: English'}")

    def show_with_animation(self):
        """Show the floating bar with animation."""
        self.text_input.clear()
        self.show()
        self.raise_()
        self.activateWindow()
        self.text_input.setFocus()

        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.WIDTH) // 2
        y = int(screen.height() * 0.25)

        start_rect = QRect(x, y + 20, self.WIDTH, self.HEIGHT_COLLAPSED)
        end_rect = QRect(x, y, self.WIDTH, self.HEIGHT_COLLAPSED)

        self.setGeometry(start_rect)
        self._show_anim.setStartValue(start_rect)
        self._show_anim.setEndValue(end_rect)
        self._show_anim.start()

    def hide_with_animation(self):
        """Hide the floating bar with animation."""
        rect = self.geometry()
        end_rect = QRect(rect.x(), rect.y() + 20, rect.width(), rect.height())
        self._hide_anim.setStartValue(rect)
        self._hide_anim.setEndValue(end_rect)
        self._hide_anim.start()

    def expand(self):
        """Expand to show log area."""
        if self._expanded:
            return
        self._expanded = True
        self.log_area.setVisible(True)
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.WIDTH) // 2
        y = int(screen.height() * 0.25)

        anim = QPropertyAnimation(self, b"geometry")
        anim.setDuration(200)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.setStartValue(self.geometry())
        anim.setEndValue(QRect(x, y, self.WIDTH, self.HEIGHT_EXPANDED))
        anim.start()
        self._expand_anim = anim

    def collapse(self):
        """Collapse to hide log area."""
        if not self._expanded:
            return
        self._expanded = False
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.WIDTH) // 2
        y = int(screen.height() * 0.25)

        anim = QPropertyAnimation(self, b"geometry")
        anim.setDuration(200)
        anim.setEasingCurve(QEasingCurve.Type.InCubic)
        anim.setStartValue(self.geometry())
        anim.setEndValue(QRect(x, y, self.WIDTH, self.HEIGHT_COLLAPSED))
        anim.finished.connect(lambda: self.log_area.setVisible(False))
        anim.start()
        self._expand_anim = anim

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            if self._expanded:
                self.collapse()
            else:
                self.hide_with_animation()
        elif event.key() == Qt.Key.Key_Down and not self._expanded:
            self.expand()
        elif event.key() == Qt.Key.Key_Up and self._expanded:
            self.collapse()
        else:
            super().keyPressEvent(event)

    def start_voice_thread(self):
        self.voice_thread = VoiceThread(self.recognizer, self.wake_detector)
        self.voice_thread.session_started.connect(self._on_session_start)
        self.voice_thread.session_ended.connect(self._on_session_end)
        self.voice_thread.speech_detected.connect(self._on_speech)
        self.voice_thread.start()

    def _on_session_start(self):
        self.show_with_animation()
        QTimer.singleShot(100, self.expand)
        self.arc_reactor.set_listening(True)
        self._log("SYSTEM", ui("session_active"))
        self.speaker.speak(ui("yes"))

    def _on_session_end(self):
        self.arc_reactor.set_listening(False)
        self._log("SYSTEM", ui("session_ended"))
        self.speaker.speak(ui("goodbye"))
        QTimer.singleShot(2000, self.hide_with_animation)

    def _on_speech(self, text):
        self._log("YOU", text)
        self.router.route(text, self.bus)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if hasattr(self, 'drag_pos') and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_pos)

    def paintEvent(self, event):
        """Draw rounded rect background."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 16, 16)
        painter.fillPath(path, QBrush(QColor(0, 0, 0, 0)))
        painter.end()
