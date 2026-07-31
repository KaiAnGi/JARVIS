"""Tests for core/logger.py secret redaction."""

from core.logger import _redact


class TestRedact:
    def test_redacts_token_key_value(self):
        assert _redact("token=abc123secret") == "[REDACTED]"

    def test_redacts_api_key_assignment(self):
        assert _redact("api_key = super-secret-value") == "[REDACTED]"

    def test_redacts_bearer_token(self):
        assert _redact("Authorization: Bearer xyz.abc.123") == "[REDACTED]"

    def test_redacts_bearer_lowercase(self):
        assert _redact("bearer abcdef0123456789") == "[REDACTED]"

    def test_redacts_plain_value_suffix(self):
        result = _redact("password= hunter2 extra")
        assert "[REDACTED]" in result

    def test_keeps_normal_text(self):
        text = "user asked for the weather today"
        assert _redact(text) == text

    def test_redacts_password_key(self):
        result = _redact("Password=hunter2")
        assert result == "[REDACTED]"
        assert "hunter2" not in result
