"""System tray icon for Jarvis."""

import os
from PIL import Image
import pystray
from pystray import MenuItem

ICON_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "jarvis.ico")


def create_icon(listening=False) -> Image.Image:
    """Load the Jarvis icon, tinted for listening state."""
    img = Image.open(ICON_PATH).convert("RGBA")
    if listening:
        r, g, b, a = img.split()
        r = r.point(lambda x: min(255, int(x * 1.3)))
        img = Image.merge("RGBA", (r, g, b, a))
    return img


class JarvisTray:
    """System tray icon with menu."""

    def __init__(self, on_show, on_quit):
        self.on_show = on_show
        self.on_quit = on_quit
        self._icon = None
        self._listening = False

    def _build_menu(self):
        return pystray.Menu(
            MenuItem("Open J.A.R.V.I.S.", self._on_show, default=True),
            MenuItem("Quit", self._on_quit)
        )

    def _on_show(self, icon, item):
        self.on_show()

    def _on_quit(self, icon, item):
        icon.stop()
        self.on_quit()

    def start(self):
        icon_img = create_icon(listening=False)
        self._icon = pystray.Icon(
            "jarvis",
            icon_img,
            "J.A.R.V.I.S.",
            self._build_menu()
        )
        self._icon.run()

    def update_listening(self, state: bool):
        self._listening = state
        if self._icon:
            self._icon.icon = create_icon(listening=state)

    def stop(self):
        if self._icon:
            self._icon.stop()
