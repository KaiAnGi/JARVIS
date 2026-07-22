"""gmail plugin - Read, send, delete, and schedule emails via Gmail API."""

import threading
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64

from googleapiclient.discovery import build

from core.credentials_manager import get_credentials
from core.language import resp

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]

_service = None
_scheduled_emails = []


def _get_service():
    global _service
    if _service is None:
        creds = get_credentials(SCOPES)
        if creds is None:
            return None
        try:
            _service = build("gmail", "v1", credentials=creds)
        except Exception as e:
            print(f"[GMAIL] Failed to build service: {e}")
            return None
    return _service


def init(bus):
    pass


def handle(action: str, text: str, bus):
    try:
        _handle(action, text, bus)
    except Exception as e:
        print(f"[GMAIL] Error: {e}")
        bus.emit("speak", resp("gmail_auth"))


def _handle(action: str, text: str, bus):
    service = _get_service()
    if service is None:
        bus.emit("speak", resp("gmail_auth"))
        return

    if action == "count_email":
        results = service.users().messages().list(
            userId="me", maxResults=5, labelIds=["INBOX", "UNREAD"]
        ).execute()
        count = len(results.get("messages", []))
        bus.emit("speak", resp("count_email", count=count))

    elif action == "check_email":
        results = service.users().messages().list(
            userId="me", maxResults=3, labelIds=["INBOX"]
        ).execute()
        messages = results.get("messages", [])
        if not messages:
            bus.emit("speak", resp("no_email"))
            return
        summaries = []
        for msg in messages:
            m = service.users().messages().get(
                userId="me", id=msg["id"], format="metadata",
                metadataHeaders=["Subject", "From"]
            ).execute()
            headers = {h["name"]: h["value"] for h in m.get("payload", {}).get("headers", [])}
            summaries.append(f"{headers.get('From', '?')}: {headers.get('Subject', '?')}")
        bus.emit("speak", resp("check_email", emails="; ".join(summaries)))

    elif action == "read_email":
        results = service.users().messages().list(
            userId="me", maxResults=1, labelIds=["INBOX"]
        ).execute()
        messages = results.get("messages", [])
        if not messages:
            bus.emit("speak", resp("no_read"))
            return
        m = service.users().messages().get(
            userId="me", id=messages[0]["id"], format="full"
        ).execute()
        headers = {h["name"]: h["value"] for h in m.get("payload", {}).get("headers", [])}
        bus.emit("speak", resp("read_email",
                                **{"from": headers.get("From", "?"),
                                   "subject": headers.get("Subject", "?")}))

    elif action == "delete_email":
        _delete_email(service, text, bus)

    elif action == "send_email":
        _send_email_interactive(service, text, bus)

    elif action == "schedule_email":
        _schedule_email(service, text, bus)


def _delete_email(service, text: str, bus):
    """Delete the most recent email or one matching a query."""
    text_lower = text.lower()
    query = None
    for prefix in ("delete email", "borra correo", "eliminar correo", "delete mail"):
        if prefix in text_lower:
            query = text_lower.split(prefix, 1)[1].strip()
            break

    if query:
        results = service.users().messages().list(
            userId="me", maxResults=5, q=query, labelIds=["INBOX"]
        ).execute()
    else:
        results = service.users().messages().list(
            userId="me", maxResults=1, labelIds=["INBOX"]
        ).execute()

    messages = results.get("messages", [])
    if not messages:
        bus.emit("speak", resp("no_email"))
        return

    msg_id = messages[0]["id"]
    service.users().messages().delete(userId="me", id=msg_id).execute()

    m = service.users().messages().get(
        userId="me", id=msg_id, format="metadata",
        metadataHeaders=["Subject"]
    ).execute()
    subject = "?"
    for h in m.get("payload", {}).get("headers", []):
        if h["name"] == "Subject":
            subject = h["value"]
            break
    bus.emit("speak", resp("email_deleted", subject=subject))


def _send_email_interactive(service, text: str, bus):
    """Send an email. Parses recipient, subject, and body from voice text."""
    text_lower = text.lower()

    to = _extract_field(text_lower, ("to ", "para ", "destinatario "))
    subject = _extract_field(text_lower, ("subject ", "asunto "))
    body = _extract_field(text_lower, ("body ", "mensaje ", "contenido "))

    if not to:
        bus.emit("speak", resp("email_who"))
        return
    if not subject:
        bus.emit("speak", resp("email_what_subject"))
        return
    if not body:
        body = "(Enviado por voz via J.A.R.V.I.S.)"

    _do_send(service, to, subject, body, bus)


def _do_send(service, to: str, subject: str, body: str, bus, speak_msg=None):
    """Actually send an email via Gmail API."""
    message = MIMEMultipart()
    message["to"] = to
    message["subject"] = subject
    message.attach(MIMEText(body, "plain"))

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("ascii")
    service.users().messages().send(
        userId="me", body={"raw": raw}
    ).execute()

    bus.emit("speak", speak_msg or resp("email_sent", to=to))


def _schedule_email(service, text: str, bus):
    """Schedule an email to be sent later."""
    text_lower = text.lower()

    to = _extract_field(text_lower, ("to ", "para ", "destinatario "))
    subject = _extract_field(text_lower, ("subject ", "asunto "))
    body = _extract_field(text_lower, ("body ", "mensaje ", "contenido "))
    time_str = _extract_field(text_lower, ("at ", "a las ", "para las "))
    if not time_str:
        time_str = _extract_field(text_lower, ("schedule ", "programa "))

    if not to:
        bus.emit("speak", resp("email_who"))
        return
    if not subject:
        bus.emit("speak", resp("email_what_subject"))
        return
    if not body:
        body = "(Enviado por voz via J.A.R.V.I.S.)"

    if not time_str:
        bus.emit("speak", resp("email_when"))
        return

    send_time = _parse_time(time_str)
    if send_time is None:
        bus.emit("speak", resp("email_time_error"))
        return

    now = datetime.now()
    if send_time <= now:
        send_time += timedelta(days=1)

    delay = (send_time - now).total_seconds()

    def _send_later():
        time.sleep(delay)
        _do_send(service, to, subject, body, bus,
                 speak_msg=resp("email_scheduled_sent", to=to, time=send_time.strftime("%H:%M")))

    threading.Thread(target=_send_later, daemon=True).start()
    _scheduled_emails.append({"to": to, "subject": subject, "time": send_time})

    bus.emit("speak", resp("email_scheduled", to=to, time=send_time.strftime("%H:%M")))


def _extract_field(text: str, prefixes: tuple) -> str:
    """Extract a field value after one of the given prefixes."""
    for prefix in sorted(prefixes, key=len, reverse=True):
        if prefix in text:
            value = text.split(prefix, 1)[1].strip()
            if value:
                return value
    return ""


def _parse_time(time_str: str):
    """Parse a time string like '14:30', '2:30 pm', 'in 5 minutes'."""
    time_str = time_str.strip().lower()
    now = datetime.now()

    if "in " in time_str:
        parts = time_str.split("in ", 1)[1].strip()
        try:
            if "hour" in parts:
                num = int("".join(c for c in parts.split("hour")[0] if c.isdigit()))
                return now + timedelta(hours=num)
            elif "minute" in parts:
                num = int("".join(c for c in parts.split("minute")[0] if c.isdigit()))
                return now + timedelta(minutes=num)
        except (ValueError, IndexError):
            pass

    for fmt in ("%H:%M", "%I:%M %p", "%I:%M"):
        try:
            t = datetime.strptime(time_str, fmt)
            return now.replace(hour=t.hour, minute=t.minute, second=0, microsecond=0)
        except ValueError:
            continue

    return None
