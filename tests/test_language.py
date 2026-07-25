"""Tests for core/language.py"""

from core.language import (
    all_patterns,
    get_lang,
    is_goodbye,
    patterns_for,
    resp,
    set_lang,
    toggle_lang,
    ui,
)


class TestLanguageState:
    def test_default_lang_is_spanish(self):
        set_lang("es")
        assert get_lang() == "es"

    def test_set_lang(self):
        set_lang("en")
        assert get_lang() == "en"

    def test_toggle_lang_es_to_en(self):
        set_lang("es")
        assert toggle_lang() == "en"

    def test_toggle_lang_en_to_es(self):
        set_lang("en")
        assert toggle_lang() == "es"


class TestUI:
    def test_ui_spanish(self):
        set_lang("es")
        assert ui("window_title") == "J.A.R.V.I.S."

    def test_ui_english(self):
        set_lang("en")
        assert ui("placeholder") == "Type a command or say 'Hey Jarvis'..."

    def test_ui_returns_string(self):
        for key in ("send", "activate", "clear"):
            assert isinstance(ui(key), str)


class TestResp:
    def test_resp_no_kwargs(self):
        set_lang("es")
        assert resp("no_email") == "No hay correos recientes"

    def test_resp_with_kwargs(self):
        set_lang("es")
        result = resp("time", time="14:30")
        assert "14:30" in result

    def test_resp_english(self):
        set_lang("en")
        result = resp("time", time="14:30")
        assert "14:30" in result

    def test_resp_all_keys_exist_es(self):
        from core.language import RESPONSES

        for key in RESPONSES["es"]:
            resp(key)

    def test_resp_all_keys_exist_en(self):
        from core.language import RESPONSES

        set_lang("en")
        for key in RESPONSES["en"]:
            resp(key)


class TestPatterns:
    def test_patterns_for_known_plugin(self):
        patterns = patterns_for("browser", "web_search")
        assert len(patterns) > 0

    def test_patterns_for_unknown_plugin(self):
        assert patterns_for("nonexistent", "action") == []

    def test_patterns_for_unknown_action(self):
        assert patterns_for("browser", "nonexistent") == []

    def test_all_patterns_returns_dict(self):
        result = all_patterns()
        assert isinstance(result, dict)
        assert "browser" in result

    def test_all_patterns_current_lang(self):
        set_lang("es")
        result = all_patterns()
        for _plugin, actions in result.items():
            for _action, patterns in actions.items():
                assert isinstance(patterns, list)


class TestIsGoodbye:
    def test_goodbye_es(self):
        set_lang("es")
        assert is_goodbye("adiós jarvis") is True

    def test_goodbye_en(self):
        set_lang("en")
        assert is_goodbye("goodbye jarvis") is True

    def test_not_goodbye(self):
        set_lang("es")
        assert is_goodbye("abre notepad") is False

    def test_goodbye_partial_match(self):
        set_lang("en")
        assert is_goodbye("goodbye") is True
