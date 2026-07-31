"""Tests for core/database.py"""


class TestDatabase:
    def test_init_creates_tables(self, tmp_db):
        # init already called by fixture, just verify it works
        tmp_db.save_conversation("YOU", "test", 1)
        results = tmp_db.get_recent_conversations(limit=5)
        assert len(results) == 1
        assert results[0]["text"] == "test"
        assert results[0]["role"] == "YOU"

    def test_save_and_get_conversations(self, tmp_db):
        tmp_db.save_conversation("YOU", "hello", 1)
        tmp_db.save_conversation("JARVIS", "hi there", 1)
        results = tmp_db.get_recent_conversations(limit=10, session_id=1)
        assert len(results) == 2
        assert results[0]["text"] == "hello"
        assert results[1]["text"] == "hi there"

    def test_conversation_context(self, tmp_db):
        tmp_db.save_conversation("YOU", "hello", 1)
        tmp_db.save_conversation("JARVIS", "hi", 1)
        ctx = tmp_db.get_conversation_context(session_id=1)
        assert "User: hello" in ctx
        assert "JARVIS: hi" in ctx

    def test_save_command(self, tmp_db):
        tmp_db.save_command("open_app", "notepad", True, 150.0)
        history = tmp_db.get_command_history()
        assert len(history) == 1
        assert history[0]["action"] == "open_app"
        assert history[0]["success"] is True

    def test_get_command_history_filter(self, tmp_db):
        tmp_db.save_command("open_app", "notepad")
        tmp_db.save_command("web_search", "cats")
        history = tmp_db.get_command_history(action="open_app")
        assert len(history) == 1
        assert history[0]["action"] == "open_app"

    def test_frequent_commands(self, tmp_db):
        for _ in range(3):
            tmp_db.save_command("open_app")
        for _ in range(1):
            tmp_db.save_command("web_search")
        freq = tmp_db.get_frequent_commands()
        assert freq[0]["action"] == "open_app"
        assert freq[0]["count"] == 3

    def test_stats(self, tmp_db):
        tmp_db.save_command("open_app", success=True)
        tmp_db.save_command("web_search", success=False)
        stats = tmp_db.get_stats()
        assert stats["total_commands"] == 2
        assert stats["successful"] == 1
        assert stats["success_rate"] == "50.0%"

    def test_stats_empty(self, tmp_db):
        stats = tmp_db.get_stats()
        assert stats["total_commands"] == 0
        assert stats["success_rate"] == "0%"

    def test_clear_command_history(self, tmp_db):
        tmp_db.save_command("open_app", "notepad")
        tmp_db.save_command("web_search", "cats")
        assert len(tmp_db.get_command_history()) == 2
        tmp_db.clear_command_history()
        assert tmp_db.get_command_history() == []
        assert tmp_db.get_stats()["total_commands"] == 0

    def test_conversations_ordered_by_id(self, tmp_db):
        tmp_db.save_conversation("YOU", "first", 1)
        tmp_db.save_conversation("YOU", "second", 1)
        tmp_db.save_conversation("YOU", "third", 1)
        results = tmp_db.get_recent_conversations(limit=2)
        assert results[0]["text"] == "second"
        assert results[1]["text"] == "third"
