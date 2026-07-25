"""Tests for plugins/clock/plugin.py"""

from datetime import datetime, timedelta

from plugins.clock import plugin


class TestExtractTime:
    def test_spanish(self):
        assert plugin._extract_time("alarma a las 14:30") == "14:30"

    def test_english(self):
        assert plugin._extract_time("alarm at 3:30") == "3:30"

    def test_no_time(self):
        assert plugin._extract_time("poner alarma") == ""


class TestExtractDuration:
    def test_minutes_en(self):
        result = plugin._extract_duration("for 5 minutes")
        assert result == timedelta(minutes=5)

    def test_hours_en(self):
        result = plugin._extract_duration("for 2 hours")
        assert result == timedelta(hours=2)

    def test_minutes_es(self):
        result = plugin._extract_duration("durante 10 minutos")
        assert result == timedelta(minutes=10)

    def test_hours_es(self):
        result = plugin._extract_duration("por 1 hora")
        assert result == timedelta(hours=1)

    def test_no_duration(self):
        assert plugin._extract_duration("temporizador") is None


class TestExtractRepetition:
    def test_daily_en(self):
        assert plugin._extract_repetition("every day") == "daily"

    def test_daily_es(self):
        assert plugin._extract_repetition("todos los días") == "daily"

    def test_weekdays_en(self):
        assert plugin._extract_repetition("weekdays") == "weekdays"

    def test_weekends_en(self):
        assert plugin._extract_repetition("weekends") == "weekends"

    def test_none(self):
        assert plugin._extract_repetition("alarma a las 8") == "none"


class TestExtractMessage:
    def test_english(self):
        assert plugin._extract_message("message wake up!") == "wake up!"

    def test_spanish(self):
        assert plugin._extract_message("mensaje hora de trabajar") == "hora de trabajar"

    def test_no_message(self):
        assert plugin._extract_message("alarma a las 8") == ""


class TestRepetitionText:
    def test_es_daily(self):
        assert "todos los días" in plugin._repetition_text("daily", "es")

    def test_en_daily(self):
        assert "every day" in plugin._repetition_text("daily", "en")

    def test_none_empty(self):
        assert plugin._repetition_text("none", "es") == ""
        assert plugin._repetition_text("none", "en") == ""


class TestFormatDuration:
    def test_hours_and_minutes(self):
        assert plugin._format_duration(timedelta(hours=1, minutes=30)) == "1h 30m"

    def test_only_minutes(self):
        assert plugin._format_duration(timedelta(minutes=5)) == "5m"

    def test_only_seconds(self):
        assert plugin._format_duration(timedelta(seconds=30)) == "30s"

    def test_zero(self):
        assert plugin._format_duration(timedelta(0)) == "0s"


class TestNextOccurrence:
    def test_daily(self):
        dt = datetime(2025, 1, 1, 8, 0)
        result = plugin._next_occurrence(dt, "daily")
        assert result == datetime(2025, 1, 2, 8, 0)

    def test_weekdays_from_friday(self):
        dt = datetime(2025, 1, 3, 8, 0)  # Friday
        result = plugin._next_occurrence(dt, "weekdays")
        assert result.weekday() == 0  # Monday

    def test_weekends_from_monday(self):
        dt = datetime(2025, 1, 6, 8, 0)  # Monday
        result = plugin._next_occurrence(dt, "weekends")
        assert result.weekday() == 5  # Saturday


class TestParseTime:
    def test_24h(self):
        result = plugin._parse_time("14:30")
        assert result is not None
        assert result.hour == 14
        assert result.minute == 30

    def test_invalid(self):
        assert plugin._parse_time("not a time") is None


class TestStopwatch:
    def setup_method(self):
        plugin._stopwatch_start = None
        plugin._stopwatch_running = False
        plugin._stopwatch_elapsed = timedelta(0)

    def test_start_and_stop(self, bus):
        plugin._start_stopwatch(bus)
        assert plugin._stopwatch_running is True
        plugin._stop_stopwatch(bus)
        assert plugin._stopwatch_running is False

    def test_read_not_started(self, bus):
        plugin._read_stopwatch(bus)
        emitted = bus.emit.call_args[0]
        assert "not_started" in emitted[1] or "no se ha iniciado" in emitted[1]

    def test_reset(self, bus):
        plugin._start_stopwatch(bus)
        plugin._reset_stopwatch(bus)
        assert plugin._stopwatch_running is False
        assert plugin._stopwatch_elapsed == timedelta(0)

    def test_double_start(self, bus):
        plugin._start_stopwatch(bus)
        plugin._start_stopwatch(bus)
        emitted = bus.emit.call_args[0]
        assert "running" in emitted[1] or "marcha" in emitted[1]

    def test_stop_not_running(self, bus):
        plugin._stop_stopwatch(bus)
        emitted = bus.emit.call_args[0]
        assert "not_running" in emitted[1] or "no está en marcha" in emitted[1]
