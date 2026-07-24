"""Custom HUD widgets for Jarvis GUI."""

import math
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QRadialGradient, QFont
from PyQt6.QtWidgets import QWidget

from gui.styles import PRIMARY_COLOR, SECONDARY_COLOR, TEXT_COLOR


class ArcReactor(QWidget):
    """Circular arc reactor indicator that pulses when listening."""

    def __init__(self, parent=None, size=200):
        super().__init__(parent)
        self.size = size
        self.setFixedSize(size, size)
        self._angle = 0
        self._pulse = 0
        self._listening = False
        self._glow_intensity = 0

        self._timer = QTimer()
        self._timer.timeout.connect(self._animate)
        self._timer.start(30)

    def set_listening(self, state: bool):
        self._listening = state

    def _animate(self):
        self._angle = (self._angle + 3) % 360
        if self._listening:
            self._pulse = (self._pulse + 8) % 360
            self._glow_intensity = min(1.0, self._glow_intensity + 0.05)
        else:
            self._glow_intensity = max(0.0, self._glow_intensity - 0.03)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx, cy = self.size / 2, self.size / 2
        radius = self.size / 2 - 10

        # Outer ring glow
        if self._glow_intensity > 0:
            glow_color = QColor(PRIMARY_COLOR)
            glow_color.setAlphaF(self._glow_intensity * 0.3)
            for i in range(3):
                pen = QPen(glow_color)
                pen.setWidthF(2 + i * 2)
                painter.setPen(pen)
                painter.drawEllipse(QPointF(cx, cy), radius + 5 + i * 3, radius + 5 + i * 3)

        # Outer ring
        outer_pen = QPen(QColor(PRIMARY_COLOR))
        outer_pen.setWidthF(2)
        painter.setPen(outer_pen)
        painter.drawEllipse(QPointF(cx, cy), radius, radius)

        # Rotating arcs
        arc_pen = QPen(QColor(SECONDARY_COLOR))
        arc_pen.setWidthF(3)
        arc_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(arc_pen)

        rect = QRectF(cx - radius + 15, cy - radius + 15, (radius - 15) * 2, (radius - 15) * 2)
        painter.drawArc(rect, int(self._angle * 16), int(90 * 16))

        rect2 = QRectF(cx - radius + 25, cy - radius + 25, (radius - 25) * 2, (radius - 25) * 2)
        painter.drawArc(rect2, int(-self._angle * 16 + 180 * 16), int(60 * 16))

        # Inner circle
        inner_radius = radius * 0.4
        gradient = QRadialGradient(cx, cy, inner_radius)
        if self._listening:
            gradient.setColorAt(0, QColor(PRIMARY_COLOR))
            gradient.setColorAt(0.7, QColor(PRIMARY_COLOR).darker(150))
            gradient.setColorAt(1, QColor(PRIMARY_COLOR).darker(300))
        else:
            gradient.setColorAt(0, QColor(PRIMARY_COLOR).darker(200))
            gradient.setColorAt(1, QColor(PRIMARY_COLOR).darker(400))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(QPointF(cx, cy), inner_radius, inner_radius)

        # Center dot
        painter.setBrush(QBrush(QColor(SECONDARY_COLOR) if self._listening else QColor(PRIMARY_COLOR).darker(200)))
        painter.drawEllipse(QPointF(cx, cy), 5, 5)

        # Label
        painter.setPen(QColor(TEXT_COLOR if self._listening else "#666666"))
        font = QFont("Segoe UI", 10, QFont.Weight.Bold)
        painter.setFont(font)
        label = "LISTENING" if self._listening else "STANDBY"
        painter.drawText(QRectF(0, cy + radius + 10, self.size, 30), Qt.AlignmentFlag.AlignCenter, label)

        painter.end()


class StatusIndicator(QWidget):
    """Small status dot with label."""

    def __init__(self, label: str, color: str = PRIMARY_COLOR, parent=None):
        super().__init__(parent)
        self.label = label
        self.color = QColor(color)
        self.active = False
        self.setFixedHeight(24)

    def set_active(self, state: bool):
        self.active = state
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Dot
        dot_color = self.color if self.active else QColor("#333333")
        painter.setBrush(QBrush(dot_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(10, 12), 4, 4)

        # Label
        painter.setPen(QColor(TEXT_COLOR) if self.active else QColor("#555555"))
        painter.drawText(22, 16, self.label)
        painter.end()
