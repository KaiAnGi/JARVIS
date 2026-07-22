"""calendar plugin - Google Calendar events."""

from datetime import datetime, timezone, timedelta

from googleapiclient.discovery import build

from core.credentials_manager import get_credentials
from core.language import resp, get_lang

SCOPES = ["https://www.googleapis.com/auth/calendar"]

_service = None

MONTHS_ES = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
    5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
    9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
}


def _get_service():
    global _service
    if _service is None:
        creds = get_credentials(SCOPES)
        if creds is None:
            return None
        try:
            _service = build("calendar", "v3", credentials=creds)
        except Exception as e:
            print(f"[CALENDAR] Failed to build service: {e}")
            return None
    return _service


def _format_date(date_str: str) -> str:
    try:
        if "T" in date_str:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        else:
            dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        
        now = datetime.now(timezone.utc)
        today = now.date()
        event_date = dt.date()
        diff = (event_date - today).days
        
        if get_lang() == "es":
            day = dt.day
            month = MONTHS_ES[dt.month]
            if diff == 0:
                return "hoy"
            elif diff == 1:
                return "mañana"
            elif diff == -1:
                return "ayer"
            else:
                return f"{day} de {month}"
        else:
            if diff == 0:
                return "today"
            elif diff == 1:
                return "tomorrow"
            elif diff == -1:
                return "yesterday"
            else:
                return dt.strftime("%B %d")
    except Exception:
        return date_str


def init(bus):
    pass


def handle(action: str, text: str, bus):
    try:
        _handle(action, text, bus)
    except Exception as e:
        print(f"[CALENDAR] Error: {e}")
        bus.emit("speak", resp("cal_auth"))


def _handle(action: str, text: str, bus):
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
            date_str = _format_date(start)
            summaries.append(f"{e['summary']} {date_str}")
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
        date_str = _format_date(start)
        bus.emit("speak", resp("next_event", event=e["summary"], time=date_str))

    elif action == "create_event":
        bus.emit("speak", resp("create_event"))
