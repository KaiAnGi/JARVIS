"""Discord notification plugin — send messages via Discord webhook."""

import json
import os
import urllib.request
from core.language import resp

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")


def init(bus):
    if not WEBHOOK_URL:
        print("[DISCORD_NOTIFY] No DISCORD_WEBHOOK_URL set — plugin disabled")


def handle(action: str, text: str, bus):
    if not WEBHOOK_URL:
        bus.emit("speak", resp("discord_not_configured"))
        return

    if action == "discord_send":
        message = _extract_message(text, ("send to discord", "discord", "enviar a discord", "notificar"))
        if message:
            _send_webhook(message, bus)
        else:
            bus.emit("speak", resp("discord_send_what"))

    elif action == "discord_notify":
        message = _extract_message(text, ("notify discord", "notifica", "avisa a discord"))
        if message:
            _send_webhook(f"**Notificación:** {message}", bus)
        else:
            bus.emit("speak", resp("discord_send_what"))


def _send_webhook(message: str, bus):
    try:
        payload = json.dumps({"content": message}).encode("utf-8")
        req = urllib.request.Request(
            WEBHOOK_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp_:
            if resp_.status in (200, 204):
                bus.emit("speak", resp("discord_sent"))
            else:
                bus.emit("speak", resp("discord_error"))
    except Exception as e:
        print(f"[DISCORD_NOTIFY] Error: {e}")
        bus.emit("speak", resp("discord_error"))


def _extract_message(text: str, keywords: tuple) -> str:
    lower = text.lower()
    for kw in keywords:
        idx = lower.find(kw)
        if idx != -1:
            after = text[idx + len(kw):].strip()
            if after:
                return after
    return ""
