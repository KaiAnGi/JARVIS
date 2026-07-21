"""System tray icon for Jarvis."""

import math
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem


def create_icon(listening=False) -> Image.Image:
    """Generate an Iron Man mask icon programmatically."""
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Mask outline
    mask_color = (255, 107, 0, 255)  # Iron Man orange
    eye_color = (0, 212, 255, 255) if listening else (255, 107, 0, 200)

    # Head shape (rounded rectangle approximation)
    draw.rounded_rectangle(
        [8, 4, 56, 60],
        radius=15,
        fill=(30, 30, 40, 255),
        outline=mask_color,
        width=2
    )

    # Face plate
    draw.rounded_rectangle(
        [14, 12, 50, 48],
        radius=10,
        fill=(50, 50, 60, 255),
        outline=mask_color,
        width=1
    )

    # Eyes (glowing)
    eye_y = 24
    for ex in [22, 42]:
        # Glow effect
        for i in range(3):
            alpha = 80 - i * 25
            glow = (*eye_color[:3], alpha)
            draw.ellipse([ex - 4 - i, eye_y - 3 - i, ex + 4 + i, eye_y + 3 + i], fill=glow)
        draw.ellipse([ex - 4, eye_y - 3, ex + 4, eye_y + 3], fill=eye_color)

    # Mouth slit
    draw.line([24, 40, 40, 40], fill=mask_color, width=1)

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
