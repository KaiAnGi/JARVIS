"""Screenshot plugin — take screenshots and save them."""

import os
import time
from pathlib import Path

import pyautogui
from core.language import resp

SCREENSHOT_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "screenshots"


def init(bus):
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def handle(action: str, text: str, bus):
    if action == "take_screenshot":
        try:
            ts = time.strftime("%Y%m%d_%H%M%S")
            path = SCREENSHOT_DIR / f"screenshot_{ts}.png"
            pyautogui.screenshot(str(path))
            bus.emit("speak", resp("screenshot_saved", path=str(path)))
        except Exception as e:
            bus.emit("speak", resp("screenshot_error"))

    elif action == "screenshot_area":
        try:
            ts = time.strftime("%Y%m%d_%H%M%S")
            path = SCREENSHOT_DIR / f"region_{ts}.png"
            region = pyautogui.region_grabber((0, 0, 800, 600))
            region.save(str(path))
            bus.emit("speak", resp("screenshot_saved", path=str(path)))
        except Exception:
            bus.emit("speak", resp("screenshot_error"))
