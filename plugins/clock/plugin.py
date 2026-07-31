"""clock plugin - Alarms, timer, and stopwatch."""

import threading
from datetime import datetime, timedelta

from core.language import get_lang, resp

_alarms: list[dict] = []
_alarms_lock = threading.Lock()
_timer_thread = None
_timer_cancel = threading.Event()
_timer_generation = 0
_stopwatch_lock = threading.Lock()
_stopwatch_start = None
_stopwatch_running = False
_stopwatch_elapsed = timedelta(0)

_ACTIONS = {
    "set_alarm": lambda text, bus: _set_alarm(text, bus),
    "cancel_alarm": lambda text, bus: _cancel_alarm(text, bus),
    "list_alarms": lambda text, bus: _list_alarms(bus),
    "start_timer": lambda text, bus: _start_timer(text, bus),
    "stop_timer": lambda text, bus: _stop_timer(bus),
    "start_stopwatch": lambda text, bus: _start_stopwatch(bus),
    "stop_stopwatch": lambda text, bus: _stop_stopwatch(bus),
    "reset_stopwatch": lambda text, bus: _reset_stopwatch(bus),
    "read_stopwatch": lambda text, bus: _read_stopwatch(bus),
}


def init(bus):
    pass


def handle(action: str, text: str, bus):
    handler = _ACTIONS.get(action)
    if handler:
        handler(text, bus)


# ── Alarms ──────────────────────────────────────────────────────────


def _set_alarm(text: str, bus):
    text_lower = text.lower()
    lang = get_lang()

    time_str = _extract_time(text_lower)
    if not time_str:
        bus.emit("speak", resp("alarm_when"))
        return

    alarm_time = _parse_time(time_str)
    if alarm_time is None:
        bus.emit("speak", resp("alarm_time_error"))
        return

    now = datetime.now()
    if alarm_time <= now:
        alarm_time += timedelta(days=1)

    repetition = _extract_repetition(text_lower)

    message = _extract_message(text_lower)
    if not message:
        message = resp("alarm_default_msg")

    alarm = {
        "time": alarm_time,
        "message": message,
        "repetition": repetition,
        "event": threading.Event(),
    }
    with _alarms_lock:
        alarm["id"] = len(_alarms)
        _alarms.append(alarm)

    _schedule_alarm(alarm, bus)

    rep_text = _repetition_text(repetition, lang)
    bus.emit("speak", resp("alarm_set", time=alarm_time.strftime("%H:%M"), repetition=rep_text))


def _schedule_alarm(alarm: dict, bus):
    def _alarm_thread():
        while True:
            now = datetime.now()
            target = alarm["time"]
            if target <= now:
                if alarm["repetition"] == "none":
                    break
                alarm["time"] = _next_occurrence(target, alarm["repetition"])
                continue

            wait_seconds = (target - now).total_seconds()
            if alarm["event"].wait(wait_seconds):
                return

            if datetime.now() >= target:
                bus.emit("speak", alarm["message"])

                if alarm["repetition"] == "none":
                    with _alarms_lock:
                        if alarm in _alarms:
                            _alarms.remove(alarm)
                    break
                else:
                    alarm["time"] = _next_occurrence(alarm["time"], alarm["repetition"])

    t = threading.Thread(target=_alarm_thread, daemon=True)
    t.start()


def _next_occurrence(dt: datetime, repetition: str) -> datetime:
    if repetition == "daily":
        return dt + timedelta(days=1)
    elif repetition == "weekdays":
        next_day = dt + timedelta(days=1)
        while next_day.weekday() >= 5:
            next_day += timedelta(days=1)
        return next_day
    elif repetition == "weekends":
        next_day = dt + timedelta(days=1)
        while next_day.weekday() < 5:
            next_day += timedelta(days=1)
        return next_day
    return dt + timedelta(days=1)


def _cancel_alarm(text: str, bus):
    text_lower = text.lower()

    with _alarms_lock:
        if "all" in text_lower or "todos" in text_lower or "todas" in text_lower:
            count = len(_alarms)
            for alarm in _alarms:
                alarm["event"].set()
            _alarms.clear()
            bus.emit("speak", resp("alarm_cancel_all", count=count))
            return

        if _alarms:
            alarm = _alarms.pop()
            alarm["event"].set()
            bus.emit("speak", resp("alarm_cancelled", time=alarm["time"].strftime("%H:%M")))
        else:
            bus.emit("speak", resp("alarm_none"))


def _list_alarms(bus):
    with _alarms_lock:
        alarms_snapshot = list(_alarms)

    if not alarms_snapshot:
        bus.emit("speak", resp("alarm_none"))
        return

    summaries = []
    for a in alarms_snapshot:
        rep = _repetition_text(a["repetition"], get_lang())
        summaries.append(f"{a['time'].strftime('%H:%M')} {rep}")

    bus.emit("speak", resp("alarm_list", alarms=", ".join(summaries)))


# ── Timer ───────────────────────────────────────────────────────────


def _start_timer(text: str, bus):
    global _timer_thread, _timer_cancel, _timer_generation

    text_lower = text.lower()
    duration = _extract_duration(text_lower)
    if duration is None:
        bus.emit("speak", resp("timer_how_long"))
        return

    _timer_cancel.set()
    _timer_cancel.clear()
    _timer_generation += 1
    generation = _timer_generation

    def _timer_thread_fn():
        _timer_cancel.wait(duration.total_seconds())
        if not _timer_cancel.is_set() and generation == _timer_generation:
            bus.emit("speak", resp("timer_done"))

    _timer_thread = threading.Thread(target=_timer_thread_fn, daemon=True)
    _timer_thread.start()

    bus.emit("speak", resp("timer_started", time=_format_duration(duration)))


def _stop_timer(bus):
    global _timer_cancel, _timer_generation
    _timer_cancel.set()
    _timer_generation += 1
    bus.emit("speak", resp("timer_stopped"))


# ── Stopwatch ───────────────────────────────────────────────────────


def _start_stopwatch(bus):
    global _stopwatch_start, _stopwatch_running, _stopwatch_elapsed

    with _stopwatch_lock:
        if _stopwatch_running:
            bus.emit("speak", resp("stopwatch_running"))
            return

        _stopwatch_start = datetime.now() - _stopwatch_elapsed
        _stopwatch_running = True
    bus.emit("speak", resp("stopwatch_started"))


def _stop_stopwatch(bus):
    global _stopwatch_running, _stopwatch_elapsed

    with _stopwatch_lock:
        if not _stopwatch_running:
            bus.emit("speak", resp("stopwatch_not_running"))
            return

        if _stopwatch_start is not None:
            _stopwatch_elapsed = datetime.now() - _stopwatch_start
        _stopwatch_running = False
    bus.emit("speak", resp("stopwatch_stopped", time=_format_duration(_stopwatch_elapsed)))


def _reset_stopwatch(bus):
    global _stopwatch_start, _stopwatch_running, _stopwatch_elapsed

    with _stopwatch_lock:
        _stopwatch_start = None
        _stopwatch_running = False
        _stopwatch_elapsed = timedelta(0)
    bus.emit("speak", resp("stopwatch_reset"))


def _read_stopwatch(bus):
    with _stopwatch_lock:
        running = _stopwatch_running
        start = _stopwatch_start
        elapsed = _stopwatch_elapsed

    if running and start is not None:
        current = datetime.now() - start
        bus.emit("speak", resp("stopwatch_elapsed", time=_format_duration(current)))
    elif elapsed > timedelta(0):
        bus.emit("speak", resp("stopwatch_paused", time=_format_duration(elapsed)))
    else:
        bus.emit("speak", resp("stopwatch_not_started"))


# ── Helpers ─────────────────────────────────────────────────────────


def _extract_time(text: str) -> str:
    for prefix in ("a las ", "for ", "at ", "para las "):
        if prefix in text:
            value = text.split(prefix, 1)[1].strip()
            if value:
                time_parts = value.split()
                if time_parts:
                    return time_parts[0]
    return ""


def _extract_duration(text: str) -> timedelta | None:
    for prefix in ("for ", "durante ", "por ", "timer ", "temporizador "):
        if prefix in text:
            text = text.split(prefix, 1)[1].strip()
            break

    total_seconds = 0
    remaining = text

    if "hour" in text or "hora" in text:
        try:
            before = text.split("hour")[0] if "hour" in text else text.split("hora")[0]
            num_str = "".join(c for c in before if c.isdigit())
            total_seconds += int(num_str) * 3600
        except (ValueError, IndexError):
            pass
        idx = text.find("hour") if "hour" in text else text.find("hora")
        remaining = text[idx:]

    if "minute" in remaining or "minuto" in remaining:
        try:
            before = remaining.split("minute")[0] if "minute" in remaining else remaining.split("minuto")[0]
            num_str = "".join(c for c in before if c.isdigit())
            total_seconds += int(num_str) * 60
        except (ValueError, IndexError):
            pass
        idx = remaining.find("minute") if "minute" in remaining else remaining.find("minuto")
        remaining = remaining[idx:]

    if "second" in remaining or "segundo" in remaining:
        try:
            before = remaining.split("second")[0] if "second" in remaining else remaining.split("segundo")[0]
            num_str = "".join(c for c in before if c.isdigit())
            total_seconds += int(num_str)
        except (ValueError, IndexError):
            pass

    if total_seconds == 0:
        nums = "".join(c for c in text if c.isdigit() or c == " ")
        parts = nums.split()
        if parts:
            try:
                total_seconds = int(parts[0]) * 60
            except ValueError:
                return None
        else:
            return None

    return timedelta(seconds=total_seconds) if total_seconds > 0 else None


def _extract_repetition(text: str) -> str:
    if "every day" in text or "todos los días" in text or "cada día" in text:
        return "daily"
    if "weekdays" in text or "entre semana" in text or "días de semana" in text:
        return "weekdays"
    if "weekends" in text or "fines de semana" in text:
        return "weekends"
    return "none"


def _extract_message(text: str) -> str:
    for prefix in ("message ", "mensaje ", "says ", "dice "):
        if prefix in text:
            return text.split(prefix, 1)[1].strip()
    return ""


def _repetition_text(repetition: str, lang: str) -> str:
    if lang == "es":
        return {
            "none": "",
            "daily": "(todos los días)",
            "weekdays": "(entre semana)",
            "weekends": "(fines de semana)",
        }.get(repetition, "")
    else:
        return {
            "none": "",
            "daily": "(every day)",
            "weekdays": "(weekdays)",
            "weekends": "(weekends)",
        }.get(repetition, "")


def _format_duration(td: timedelta) -> str:
    total = int(td.total_seconds())
    hours = total // 3600
    minutes = (total % 3600) // 60
    seconds = total % 60

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")

    return " ".join(parts)


def _parse_time(time_str: str) -> datetime | None:
    now = datetime.now()
    time_str = time_str.strip().lower()

    for fmt in ("%H:%M", "%I:%M %p", "%I:%M", "%H", "%I"):
        try:
            t = datetime.strptime(time_str, fmt)
            return now.replace(hour=t.hour, minute=t.minute, second=0, microsecond=0)
        except ValueError:
            continue

    return None
