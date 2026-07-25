"""Tests for plugins/datetime_calc/plugin.py"""

from datetime import datetime

from core.language import set_lang
from plugins.datetime_calc import plugin


class TestWordsToNumber:
    def test_english_words(self):
        result = plugin._words_to_number("five plus three")
        assert "5" in result
        assert "3" in result

    def test_spanish_words(self):
        result = plugin._words_to_number("cinco más tres")
        assert "5" in result
        assert "3" in result

    def test_already_numbers(self):
        assert plugin._words_to_number("5 + 3") == "5 + 3"

    def test_large_numbers(self):
        result = plugin._words_to_number("one hundred")
        assert "100" in result

    def test_ten(self):
        result = plugin._words_to_number("ten plus five")
        assert "10" in result
        assert "5" in result

    def test_spanish_large(self):
        result = plugin._words_to_number("cien más cincuenta")
        assert "100" in result
        assert "50" in result


class TestCalculate:
    def test_addition(self):
        assert plugin._calculate("calculate 2 plus 3") == 5

    def test_subtraction(self):
        assert plugin._calculate("what is 10 minus 4") == 6

    def test_multiplication(self):
        assert plugin._calculate("calculate 6 times 7") == 42

    def test_division(self):
        assert plugin._calculate("what is 10 divided by 2") == 5.0

    def test_spanish_addition(self):
        assert plugin._calculate("cuánto es 2 más 3") == 5

    def test_spanish_subtraction(self):
        assert plugin._calculate("calcular 10 menos 4") == 6

    def test_word_numbers(self):
        result = plugin._calculate("calculate five plus three")
        assert result == 8

    def test_no_match(self):
        assert plugin._calculate("hello world") is None

    def test_division_by_zero(self):
        result = plugin._calculate("calculate 5 divided by 0")
        assert result is None

    def test_floating_point(self):
        result = plugin._calculate("calculate 3.5 plus 1.5")
        assert result == 5.0

    def test_complex_expression_sequential(self):
        # Sequential evaluation: 2+3=5, 5*4=20
        result = plugin._calculate("calculate 2 plus 3 times 4")
        assert result == 20

    def test_over_division(self):
        result = plugin._calculate("what is 10 over 2")
        assert result == 5.0

    def test_no_tokens(self):
        result = plugin._calculate("calculate plus times")
        assert result is None


class TestHandle:
    def test_get_time(self, bus):
        set_lang("es")
        plugin.handle("get_time", "", bus)
        bus.emit.assert_called_once()
        event, msg = bus.emit.call_args[0]
        assert event == "speak"
        # Should contain a time-like pattern
        assert ":" in msg or "AM" in msg or "PM" in msg or "am" in msg or "pm" in msg

    def test_get_date_es(self, bus):
        set_lang("es")
        plugin.handle("get_date", "", bus)
        bus.emit.assert_called_once()
        event, msg = bus.emit.call_args[0]
        assert event == "speak"
        # Should contain the year
        year = str(datetime.now().year)
        assert year in msg

    def test_get_date_en(self, bus):
        set_lang("en")
        plugin.handle("get_date", "", bus)
        bus.emit.assert_called_once()
        event, msg = bus.emit.call_args[0]
        assert event == "speak"
        year = str(datetime.now().year)
        assert year in msg

    def test_calculate_valid(self, bus):
        set_lang("es")
        plugin.handle("calculate", "calculate 2 plus 2", bus)
        event, msg = bus.emit.call_args[0]
        assert event == "speak"
        assert "4" in str(msg)

    def test_calculate_invalid(self, bus):
        set_lang("es")
        plugin.handle("calculate", "calculate abc", bus)
        event, msg = bus.emit.call_args[0]
        assert event == "speak"
        assert isinstance(msg, str)
        assert len(msg) > 0

    def test_calculate_division_by_zero(self, bus):
        set_lang("es")
        plugin.handle("calculate", "calculate 5 divided by 0", bus)
        bus.emit.assert_called_once()
        event, _msg = bus.emit.call_args[0]
        assert event == "speak"
