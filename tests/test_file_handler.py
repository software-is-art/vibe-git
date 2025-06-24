"""Tests for VibeFileHandler to achieve 100% mutation coverage"""

from pathlib import Path
from threading import Event
from unittest.mock import MagicMock, patch
import time

import pytest
from beartype.roar import BeartypeException

from vibe_git.main import VibeFileHandler


class TestVibeFileHandler:
    """Test suite for VibeFileHandler to kill all mutations"""

    def test_init_with_valid_git_repo(self, tmp_path):
        """Test initialization with valid git repo"""
        # Create a git repo
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        
        # Create handler
        commit_event = Event()
        handler = VibeFileHandler(tmp_path, commit_event)
        
        assert handler.repo_path == tmp_path
        assert handler.commit_event == commit_event
        assert handler.min_commit_interval == 0.0
        assert handler.last_commit_time == 0

    def test_init_with_invalid_repo_raises_beartype_error(self, tmp_path):
        """Test initialization with non-git directory raises BeartypeException"""
        # Don't create .git directory
        commit_event = Event()
        
        with pytest.raises(BeartypeException):
            VibeFileHandler(tmp_path, commit_event)

    def test_should_ignore_git_internal_paths(self, tmp_path):
        """Test that .git internal paths are ignored"""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        
        handler = VibeFileHandler(tmp_path, Event())
        
        # Test various .git paths
        assert handler.should_ignore_path(".git/objects/abc")
        assert handler.should_ignore_path(str(tmp_path / ".git" / "refs"))
        assert handler.should_ignore_path(".git/")
        
    def test_should_ignore_absolute_paths_outside_repo(self, tmp_path):
        """Test that paths outside the repo are ignored"""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        
        handler = VibeFileHandler(tmp_path, Event())
        
        # Path outside repo
        outside_path = tmp_path.parent / "outside.txt"
        assert handler.should_ignore_path(str(outside_path))

    @patch('vibe_git.main.run_git_command')
    def test_should_ignore_gitignored_files(self, mock_run_git_command, tmp_path):
        """Test that gitignored files are properly ignored"""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        
        handler = VibeFileHandler(tmp_path, Event())
        
        # Mock git check-ignore returning success (file is ignored)
        mock_run_git_command.return_value = (True, "")
        
        assert handler.should_ignore_path("node_modules/package.json")
        mock_run_git_command.assert_called_with(
            ["check-ignore", "node_modules/package.json"], tmp_path
        )

    @patch('vibe_git.main.run_git_command')
    def test_should_not_ignore_non_gitignored_files(self, mock_run_git_command, tmp_path):
        """Test that non-gitignored files are not ignored"""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        
        handler = VibeFileHandler(tmp_path, Event())
        
        # Mock git check-ignore returning failure (file is not ignored)
        mock_run_git_command.return_value = (False, "")
        
        assert not handler.should_ignore_path("src/main.py")
        mock_run_git_command.assert_called_with(
            ["check-ignore", "src/main.py"], tmp_path
        )

    def test_on_any_event_ignores_directories(self, tmp_path):
        """Test that directory events are ignored"""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        
        commit_event = Event()
        handler = VibeFileHandler(tmp_path, commit_event)
        
        # Create mock directory event
        event = MagicMock()
        event.is_directory = True
        event.src_path = "some/directory"
        
        handler.on_any_event(event)
        
        # Commit event should not be set
        assert not commit_event.is_set()

    @patch('vibe_git.main.run_git_command')
    def test_on_any_event_ignores_gitignored_files(self, mock_run_git_command, tmp_path):
        """Test that events for gitignored files are ignored"""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        
        commit_event = Event()
        handler = VibeFileHandler(tmp_path, commit_event)
        
        # Mock git check-ignore to return success (file is ignored)
        mock_run_git_command.return_value = (True, "")
        
        # Create mock file event
        event = MagicMock()
        event.is_directory = False
        event.src_path = "node_modules/file.js"
        
        handler.on_any_event(event)
        
        # Commit event should not be set
        assert not commit_event.is_set()

    def test_on_any_event_respects_rate_limiting(self, tmp_path):
        """Test that rate limiting prevents rapid commits"""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        
        commit_event = Event()
        handler = VibeFileHandler(tmp_path, commit_event)
        
        # Set last commit time to recent
        handler.last_commit_time = time.time() - 0.5  # Half second ago
        
        # Create mock file event
        event = MagicMock()
        event.is_directory = False
        event.src_path = "file.txt"
        
        # Mock should_ignore_path to return False
        with patch.object(handler, 'should_ignore_path', return_value=False):
            handler.on_any_event(event)
        
        # Commit event should not be set due to rate limiting
        assert not commit_event.is_set()

    def test_on_any_event_sets_commit_event_after_interval(self, tmp_path):
        """Test that commit event is set after minimum interval"""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        
        commit_event = Event()
        handler = VibeFileHandler(tmp_path, commit_event)
        
        # Set last commit time to more than 1 second ago
        handler.last_commit_time = time.time() - 2
        
        # Create mock file event
        event = MagicMock()
        event.is_directory = False
        event.src_path = "file.txt"
        
        # Mock should_ignore_path to return False
        with patch.object(handler, 'should_ignore_path', return_value=False):
            handler.on_any_event(event)
        
        # Commit event should be set
        assert commit_event.is_set()
        # Last commit time should be updated
        assert handler.last_commit_time > time.time() - 1

    def test_on_any_event_with_git_internal_file(self, tmp_path):
        """Test handling of .git internal file events"""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        
        commit_event = Event()
        handler = VibeFileHandler(tmp_path, commit_event)
        
        # Create mock file event for .git internal file
        event = MagicMock()
        event.is_directory = False
        event.src_path = str(tmp_path / ".git" / "index")
        
        handler.on_any_event(event)
        
        # Commit event should not be set
        assert not commit_event.is_set()

    @patch('vibe_git.main.run_git_command')
    def test_should_ignore_with_absolute_path_in_repo(self, mock_run_git_command, tmp_path):
        """Test should_ignore_path with absolute path inside repo"""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        
        handler = VibeFileHandler(tmp_path, Event())
        
        # Mock git check-ignore to return False (not ignored)
        mock_run_git_command.return_value = (False, "")
        
        # Test with absolute path inside repo
        file_path = tmp_path / "src" / "main.py"
        assert not handler.should_ignore_path(str(file_path))
        
        # Should call git check-ignore with relative path
        mock_run_git_command.assert_called_with(
            ["check-ignore", "src/main.py"], tmp_path
        )