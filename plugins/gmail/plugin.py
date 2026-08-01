"""gmail plugin - Read, send, delete, and schedule emails via Gmail API."""

import base64
import threading
import time
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from googleapiclient.discovery import build

from core.credentials_manager import get_credentials
from core.language import resp
from core.text_utils import extract_after_keyword

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]

_service = None
_scheduled_emails: list[dict] = []
_pending_confirm = None


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


def handle(action: str, text: str, bus):
    try:
        _handle(action, text, bus)
    except Exception as e:
        print(f"[GMAIL] Error: {e}")
        bus.emit("speak", resp("gmail_auth"))


def _handle(action: str, text: str, bus):
    global _pending_confirm

    if _pending_confirm is not None:
        answer = text.lower().strip()
        if answer in ("sí", "si", "yes", "confirmo", "confirm", "ok", "dale", "claro", "afirmativo"):
            pending = _pending_confirm
            _pending_confirm = None
            if pending["type"] == "delete":
                _execute_delete(pending["service"], pending["msg_id"], pending["subject"], bus)
            elif pending["type"] == "send":
                _execute_send(pending["service"], pending["to"], pending["subject"], pending["body"], bus)
        else:
            pending = _pending_confirm
            _pending_confirm = None
            cancel_key = "email_delete_cancelled" if pending["type"] == "delete" else "email_send_cancelled"
            bus.emit("speak", resp(cancel_key))
        return

    service = _get_service()
    if service is None:
        bus.emit("speak", resp("gmail_auth"))
        return

    if action == "count_email":
        results = service.users().messages().list(userId="me", maxResults=5, labelIds=["INBOX", "UNREAD"]).execute()
        count = len(results.get("messages", []))
        bus.emit("speak", resp("count_email", count=count))

    elif action == "check_email":
        results = service.users().messages().list(userId="me", maxResults=3, labelIds=["INBOX"]).execute()
        messages = results.get("messages", [])
        if not messages:
            bus.emit("speak", resp("no_email"))
            return
        summaries = []
        for msg in messages:
            m = (
                service.users()
                .messages()
                .get(userId="me", id=msg["id"], format="metadata", metadataHeaders=["Subject", "From"])
                .execute()
            )
            headers = {h["name"]: h["value"] for h in m.get("payload", {}).get("headers", [])}
            summaries.append(f"{headers.get('From', '?')}: {headers.get('Subject', '?')}")
        bus.emit("speak", resp("check_email", emails="; ".join(summaries)))

    elif action == "read_email":
        results = service.users().messages().list(userId="me", maxResults=1, labelIds=["INBOX"]).execute()
        messages = results.get("messages", [])
        if not messages:
            bus.emit("speak", resp("no_read"))
            return
        m = service.users().messages().get(userId="me", id=messages[0]["id"], format="full").execute()
        headers = {h["name"]: h["value"] for h in m.get("payload", {}).get("headers", [])}
        bus.emit(
            "speak", resp("read_email", **{"from": headers.get("From", "?"), "subject": headers.get("Subject", "?")})
        )

    elif action == "delete_email":
        _delete_email(service, text, bus)

    elif action == "send_email":
        _send_email_interactive(service, text, bus)

    elif action == "schedule_email":
        _schedule_email(service, text, bus)


def _delete_email(service, text: str, bus):
    """Delete the most recent email or one matching a query."""
    global _pending_confirm
    text_lower = text.lower()
    query = extract_after_keyword(text_lower, ("delete email", "borra correo", "eliminar correo", "delete mail"))

    if query:
        results = service.users().messages().list(userId="me", maxResults=5, q=query, labelIds=["INBOX"]).execute()
    else:
        results = service.users().messages().list(userId="me", maxResults=1, labelIds=["INBOX"]).execute()

    messages = results.get("messages", [])
    if not messages:
        bus.emit("speak", resp("no_email"))
        return

    msg_id = messages[0]["id"]

    m = service.users().messages().get(userId="me", id=msg_id, format="metadata", metadataHeaders=["Subject"]).execute()
    subject = "?"
    for h in m.get("payload", {}).get("headers", []):
        if h["name"] == "Subject":
            subject = h["value"]
            break

    _pending_confirm = {"type": "delete", "service": service, "msg_id": msg_id, "subject": subject}
    bus.emit("speak", resp("email_delete_confirm", subject=subject))


def _execute_delete(service, msg_id: str, subject: str, bus):
    service.users().messages().delete(userId="me", id=msg_id).execute()
    bus.emit("speak", resp("email_deleted", subject=subject))


def _send_email_interactive(service, text: str, bus):
    """Send an email. Parses recipient, subject, and body from voice text."""
    global _pending_confirm
    text_lower = text.lower()

    to = extract_after_keyword(text_lower, ("to ", "para ", "destinatario "))
    subject = extract_after_keyword(text_lower, ("subject ", "asunto "))
    body = extract_after_keyword(text_lower, ("body ", "mensaje ", "contenido "))

    if not to:
        bus.emit("speak", resp("email_who"))
        return
    if not subject:
        bus.emit("speak", resp("email_what_subject"))
        return
    if not body:
        body = "(Enviado por voz via J.A.R.V.I.S.)"

    _pending_confirm = {"type": "send", "service": service, "to": to, "subject": subject, "body": body}
    bus.emit("speak", resp("email_send_confirm", to=to, subject=subject))


def _execute_send(service, to: str, subject: str, body: str, bus):
    message = MIMEMultipart()
    message["to"] = to
    message["subject"] = subject
    message.attach(MIMEText(body, "plain"))

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("ascii")
    service.users().messages().send(userId="me", body={"raw": raw}).execute()

    bus.emit("speak", resp("email_sent", to=to))


def _schedule_email(service, text: str, bus):
    """Schedule an email to be sent later."""
    text_lower = text.lower()

    to = extract_after_keyword(text_lower, ("to ", "para ", "destinatario "))
    subject = extract_after_keyword(text_lower, ("subject ", "asunto "))
    body = extract_after_keyword(text_lower, ("body ", "mensaje ", "contenido "))
    time_str = extract_after_keyword(text_lower, ("at ", "a las ", "para las "))
    if not time_str:
        time_str = extract_after_keyword(text_lower, ("schedule ", "programa "))

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
        message = MIMEMultipart()
        message["to"] = to
        message["subject"] = subject
        message.attach(MIMEText(body, "plain"))
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode("ascii")
        service.users().messages().send(userId="me", body={"raw": raw}).execute()
        bus.emit("speak", resp("email_scheduled_sent", to=to, time=send_time.strftime("%H:%M")))

    threading.Thread(target=_send_later, daemon=True).start()
    _scheduled_emails.append({"to": to, "subject": subject, "time": send_time})

    bus.emit("speak", resp("email_scheduled", to=to, time=send_time.strftime("%H:%M")))


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
