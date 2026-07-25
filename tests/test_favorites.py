"""Tests for core/favorites.py"""


class TestFavorites:
    def test_add_and_get_app(self, tmp_favorites):
        tmp_favorites.add_app("notepad", "C:\\notepad.exe")
        apps = tmp_favorites.get_apps()
        assert "notepad" in apps
        assert apps["notepad"]["path"] == "C:\\notepad.exe"

    def test_add_search_increments_uses(self, tmp_favorites):
        tmp_favorites.add_search("python tutorials")
        tmp_favorites.add_search("Python Tutorials")
        searches = tmp_favorites.get_searches()
        assert searches["python tutorials"]["uses"] == 2

    def test_add_command(self, tmp_favorites):
        tmp_favorites.add_command("open_app", "abre notepad")
        commands = tmp_favorites.get_commands()
        assert "abre notepad" in commands
        assert commands["abre notepad"]["action"] == "open_app"
        assert commands["abre notepad"]["uses"] == 1

    def test_get_top_commands(self, tmp_favorites):
        tmp_favorites.add_command("a", "cmd1")
        tmp_favorites.add_command("b", "cmd2")
        tmp_favorites.add_command("c", "cmd2")
        top = tmp_favorites.get_top_commands(limit=1)
        assert len(top) == 1
        assert top[0]["text"] == "cmd2"
        assert top[0]["uses"] == 2

    def test_get_top_searches(self, tmp_favorites):
        tmp_favorites.add_search("a")
        tmp_favorites.add_search("b")
        tmp_favorites.add_search("b")
        top = tmp_favorites.get_top_searches(limit=1)
        assert top[0]["query"] == "b"

    def test_remove_existing(self, tmp_favorites):
        tmp_favorites.add_app("test", "/test")
        assert tmp_favorites.remove("apps", "test") is True
        assert "test" not in tmp_favorites.get_apps()

    def test_remove_nonexistent(self, tmp_favorites):
        assert tmp_favorites.remove("apps", "nonexistent") is False

    def test_search(self, tmp_favorites):
        tmp_favorites.add_command("open_app", "abre notepad")
        tmp_favorites.add_app("notepad", "/notepad")
        results = tmp_favorites.search("notepad")
        assert len(results) >= 2
        types = {r["type"] for r in results}
        assert "command" in types
        assert "app" in types

    def test_empty_favorites(self, tmp_path, monkeypatch):
        import core.favorites as fav

        fav_path = tmp_path / "fresh_favorites.json"
        monkeypatch.setattr(fav, "FAVORITES_PATH", fav_path)
        assert fav.get_apps() == {}
        assert fav.get_searches() == {}
        assert fav.get_commands() == {}

    def test_corrupt_json_returns_defaults(self, tmp_favorites, monkeypatch):
        tmp_favorites.FAVORITES_PATH.write_text("not json!!!")
        assert tmp_favorites.get_apps() == {}
