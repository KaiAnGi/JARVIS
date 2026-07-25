"""Tests for plugins/git_control/plugin.py"""

from unittest.mock import MagicMock, patch

from plugins.git_control import plugin


class TestHandle:
    def setup_method(self):
        plugin._pending_confirm = None

    @patch("plugins.git_control.plugin.Repo")
    def test_not_repo(self, MockRepo, bus):
        from git import InvalidGitRepositoryError
        MockRepo.side_effect = InvalidGitRepositoryError()
        plugin.handle("git_status", "git status", bus)
        bus.emit.assert_called_once()

    @patch("plugins.git_control.plugin.Repo")
    def test_git_status(self, MockRepo, bus):
        mock_repo = MagicMock()
        mock_repo.index.diff.return_value = []
        mock_repo.untracked_files = ["file1.txt"]
        MockRepo.return_value = mock_repo

        plugin.handle("git_status", "git status", bus)
        bus.emit.assert_called_once()
        emitted = bus.emit.call_args[0]
        assert "1" in emitted[1]

    @patch("plugins.git_control.plugin.Repo")
    def test_git_commit_ask_confirmation(self, MockRepo, bus):
        mock_repo = MagicMock()
        mock_repo.index.diff.return_value = [MagicMock(a_path="file1.py")]
        mock_repo.untracked_files = []
        MockRepo.return_value = mock_repo

        plugin.handle("git_commit", "git commit test message", bus)
        bus.emit.assert_called_once()
        assert plugin._pending_confirm is not None

    @patch("plugins.git_control.plugin.Repo")
    def test_git_commit_confirm_yes(self, MockRepo, bus):
        mock_repo = MagicMock()
        mock_repo.index.diff.return_value = []
        mock_repo.untracked_files = ["file1.txt"]
        MockRepo.return_value = mock_repo

        plugin.handle("git_commit", "git commit test", bus)
        plugin.handle("yes", "yes", bus)
        mock_repo.index.add.assert_called_once()
        mock_repo.index.commit.assert_called_once_with("test")

    @patch("plugins.git_control.plugin.Repo")
    def test_git_commit_confirm_no(self, MockRepo, bus):
        mock_repo = MagicMock()
        mock_repo.index.diff.return_value = []
        mock_repo.untracked_files = ["file1.txt"]
        MockRepo.return_value = mock_repo

        plugin.handle("git_commit", "git commit test", bus)
        bus.reset_mock()
        plugin.handle("no", "no", bus)
        mock_repo.index.add.assert_not_called()

    @patch("plugins.git_control.plugin.Repo")
    def test_git_commit_nothing_to_commit(self, MockRepo, bus):
        mock_repo = MagicMock()
        mock_repo.index.diff.return_value = []
        mock_repo.untracked_files = []
        MockRepo.return_value = mock_repo

        plugin.handle("git_commit", "git commit test", bus)
        bus.emit.assert_called_once()

    @patch("plugins.git_control.plugin.Repo")
    def test_git_push_success(self, MockRepo, bus):
        mock_repo = MagicMock()
        MockRepo.return_value = mock_repo
        plugin.handle("git_push", "git push", bus)
        mock_repo.remote().push.assert_called_once()

    @patch("plugins.git_control.plugin.Repo")
    def test_git_push_failure(self, MockRepo, bus):
        mock_repo = MagicMock()
        mock_repo.remote().push.side_effect = Exception("network error")
        MockRepo.return_value = mock_repo
        plugin.handle("git_push", "git push", bus)
        bus.emit.assert_called()
