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
        bus.emit("speak", "Gmail not authenticated. Check credentials.json in config/")
        return

    if action == "count_email":
        results = service.users().messages().list(
            userId="me", maxResults=5, labelIds=["INBOX", "UNREAD"]
        ).execute()
        count = len(results.get("messages", []))
        bus.emit("speak", f"You have {count} unread emails")

    elif action == "check_email":
        results = service.users().messages().list(
            userId="me", maxResults=3, labelIds=["INBOX"]
        ).execute()
        messages = results.get("messages", [])
        if not messages:
            bus.emit("speak", "No recent emails")
            return
        summaries = []
        for msg in messages:
            m = service.users().messages().get(
                userId="me", id=msg["id"], format="metadata",
                metadataHeaders=["Subject", "From"]
            ).execute()
            headers = {h["name"]: h["value"] for h in m.get("payload", {}).get("headers", [])}
            summaries.append(f"From {headers.get('From', 'unknown')}: {headers.get('Subject', 'no subject')}")
        bus.emit("speak", f"Recent emails: {'; '.join(summaries)}")

    elif action == "read_email":
        results = service.users().messages().list(
            userId="me", maxResults=1, labelIds=["INBOX"]
        ).execute()
        messages = results.get("messages", [])
        if not messages:
            bus.emit("speak", "No emails to read")
            return
        m = service.users().messages().get(
            userId="me", id=messages[0]["id"], format="full"
        ).execute()
        headers = {h["name"]: h["value"] for h in m.get("payload", {}).get("headers", [])}
        bus.emit("speak", f"From {headers.get('From', 'unknown')}. Subject: {headers.get('Subject', 'no subject')}")

    elif action == "send_email":
        bus.emit("speak", "Send email via voice is not yet supported for security reasons")
