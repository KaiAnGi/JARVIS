"""Iron Man HUD-style QSS themes."""

PRIMARY_COLOR = "#FF6B00"  # Iron Man orange
SECONDARY_COLOR = "#00D4FF"  # Arc reactor blue
BG_DARK = "#0A0A0F"
BG_PANEL = "#12121A"
TEXT_COLOR = "#E0E0E0"
BORDER_COLOR = "#FF6B0040"

MAIN_STYLESHEET = f"""
QMainWindow {{
    background-color: {BG_DARK};
}}
QWidget {{
    color: {TEXT_COLOR};
    font-family: 'Segoe UI', 'Consolas', monospace;
}}
QLabel {{
    background: transparent;
    border: none;
}}
QScrollBar:vertical {{
    background: {BG_DARK};
    width: 6px;
    border: none;
}}
QScrollBar::handle:vertical {{
    background: {PRIMARY_COLOR}40;
    border-radius: 3px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {PRIMARY_COLOR}80;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
"""

PANEL_STYLE = f"""
QFrame {{
    background-color: {BG_PANEL};
    border: 1px solid {PRIMARY_COLOR}30;
    border-radius: 8px;
}}
"""

BUTTON_STYLE = f"""
QPushButton {{
    background-color: {PRIMARY_COLOR}20;
    border: 1px solid {PRIMARY_COLOR}60;
    border-radius: 20px;
    color: {PRIMARY_COLOR};
    font-size: 14px;
    font-weight: bold;
    padding: 10px 24px;
}}
QPushButton:hover {{
    background-color: {PRIMARY_COLOR}40;
    border: 1px solid {PRIMARY_COLOR};
}}
QPushButton:pressed {{
    background-color: {PRIMARY_COLOR}60;
}}
"""

INPUT_STYLE = f"""
QLineEdit {{
    background-color: {BG_PANEL};
    border: 1px solid {PRIMARY_COLOR}40;
    border-radius: 6px;
    color: {TEXT_COLOR};
    padding: 8px 12px;
    font-size: 14px;
}}
QLineEdit:focus {{
    border: 1px solid {PRIMARY_COLOR};
}}
"""

LOG_STYLE = f"""
QTextEdit {{
    background-color: {BG_DARK};
    border: 1px solid {PRIMARY_COLOR}20;
    border-radius: 6px;
    color: {SECONDARY_COLOR};
    font-family: 'Consolas', monospace;
    font-size: 12px;
    padding: 8px;
}}
"""
