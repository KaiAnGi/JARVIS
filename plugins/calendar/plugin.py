"""calendar plugin - Google Calendar events."""

from datetime import datetime, timezone

from googleapiclient.discovery import build

from core.credentials_manager import get_credentials
from core.language import resp

SCOPES = ["https://www.googleapis.com/auth/calendar"]

_service = None


def _get_service():
    global _service
    if _service is None:
        creds = get_credentials(SCOPES)
        if creds is None:
            return None
        _service = build("calendar", "v3", credentials=creds)
    return _service


def init(bus):
    pass


def handle(action: str, text: str, bus):
    service = _get_service()
    if service is None:
        bus.emit("speak", resp("cal_auth"))
        return

    now = datetime.now(timezone.utc)

    if action == "list_events":
        events_result = service.events().list(
            calendarId="primary", timeMin=now.isoformat(),
            maxResults=5, singleEvents=True, orderBy="startTime"
        ).execute()
        events = events_result.get("items", [])
        if not events:
            bus.emit("speak", resp("no_events"))
            return
        summaries = []
        for e in events:
            start = e["start"].get("dateTime", e["start"].get("date"))
            summaries.append(f"{e['summary']} @ {start}")
        bus.emit("speak", resp("list_events", events="; ".join(summaries)))

    elif action == "next_event":
        events_result = service.events().list(
            calendarId="primary", timeMin=now.isoformat(),
            maxResults=1, singleEvents=True, orderBy="startTime"
        ).execute()
        events = events_result.get("items", [])
        if not events:
            bus.emit("speak", resp("no_events"))
            return
        e = events[0]
        start = e["start"].get("dateTime", e["start"].get("date"))
        bus.emit("speak", resp("next_event", event=e["summary"], time=start))

    elif action == "create_event":
        bus.emit("speak", resp("create_event"))
