"""gmail plugin - Read and send emails via Gmail API."""

import base64
from email.mime.text import MIMEText

from googleapiclient.discovery import build

from core.credentials_manager import get_credentials

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]

_service = None


def _get_service():
    global _service
    if _service is None:
        creds = get_credentials(SCOPES)
        if creds is None:
            return None
        _service = build("gmail", "v1", credentials=creds)
    return _service


def init(bus):
    pass


def handle(action: str, text: str, bus):
    service = _get_service()
    if service is None:
        bus.emit("speak", "Gmail no está autenticado. Verifica credentials.json en config/")
        return

    if action == "count_email":
        results = service.users().messages().list(
            userId="me", maxResults=5, labelIds=["INBOX", "UNREAD"]
        ).execute()
        count = len(results.get("messages", []))
        bus.emit("speak", f"Tienes {count} correos sin leer")

    elif action == "check_email":
        results = service.users().messages().list(
            userId="me", maxResults=3, labelIds=["INBOX"]
        ).execute()
        messages = results.get("messages", [])
        if not messages:
            bus.emit("speak", "No hay correos recientes")
            return
        summaries = []
        for msg in messages:
            m = service.users().messages().get(
                userId="me", id=msg["id"], format="metadata",
                metadataHeaders=["Subject", "From"]
            ).execute()
            headers = {h["name"]: h["value"] for h in m.get("payload", {}).get("headers", [])}
            summaries.append(f"De {headers.get('From', 'desconocido')}: {headers.get('Subject', 'sin asunto')}")
        bus.emit("speak", f"Correos recientes: {'; '.join(summaries)}")

    elif action == "read_email":
        results = service.users().messages().list(
            userId="me", maxResults=1, labelIds=["INBOX"]
        ).execute()
        messages = results.get("messages", [])
        if not messages:
            bus.emit("speak", "No hay correos para leer")
            return
        m = service.users().messages().get(
            userId="me", id=messages[0]["id"], format="full"
        ).execute()
        headers = {h["name"]: h["value"] for h in m.get("payload", {}).get("headers", [])}
        bus.emit("speak", f"De {headers.get('From', 'desconocido')}. Asunto: {headers.get('Subject', 'sin asunto')}")

    elif action == "send_email":
        bus.emit("speak", "Enviar correos por voz aún no está disponible por seguridad")
