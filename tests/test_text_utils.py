"""Tests for core/text_utils.py"""

from core.text_utils import extract_after_keyword


class TestExtractAfterKeyword:
    def test_basic_english(self):
        assert extract_after_keyword("search for cats", ("search for",)) == "cats"

    def test_basic_spanish(self):
        assert extract_after_keyword("busca recetas", ("busca",)) == "recetas"

    def test_multiple_keywords_returns_longest_match(self):
        text = "play on youtube metallica"
        result = extract_after_keyword(text, ("play on youtube", "play", "youtube"))
        assert result == "metallica"

    def test_no_match_returns_empty(self):
        assert extract_after_keyword("hello world", ("foo",)) == ""

    def test_keyword_at_end_returns_empty(self):
        assert extract_after_keyword("search", ("search",)) == ""

    def test_case_insensitive(self):
        assert extract_after_keyword("SEARCH for cats", ("search for",)) == "cats"

    def test_whitespace_stripped(self):
        assert extract_after_keyword("buscar   recetas", ("buscar",)) == "recetas"

    def test_empty_text(self):
        assert extract_after_keyword("", ("search",)) == ""

    def test_empty_keywords(self):
        assert extract_after_keyword("hello world", ()) == ""

    def test_preserves_original_case(self):
        result = extract_after_keyword("Search For Cats", ("search for",))
        assert result == "Cats"

    def test_multiple_occurrences_uses_first(self):
        result = extract_after_keyword("search for cats and search for dogs", ("search for",))
        assert result == "cats and search for dogs"
