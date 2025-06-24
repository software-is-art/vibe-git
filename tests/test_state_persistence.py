"""Tests for state persistence functionality"""

import json
from datetime import datetime, timedelta

from vibe_git.state_persistence import PersistedSessionState, SessionPersistence
from vibe_git.type_utils import BranchName


class TestPersistedSessionState:
    """Test the PersistedSessionState dataclass"""

    def test_to_dict(self):
        """Test conversion to dictionary"""
        state = PersistedSessionState(
            branch_name=BranchName("vibe-123"),
            session_start_time="2024-01-01T10:00:00",
            last_commit_time="2024-01-01T10:30:00",
            pr_url="https://github.com/example/repo/pull/123",
            auto_commit_enabled=True,
        )

        result = state.to_dict()

        assert result == {
            "branch_name": "vibe-123",
            "session_start_time": "2024-01-01T10:00:00",
            "last_commit_time": "2024-01-01T10:30:00",
            "pr_url": "https://github.com/example/repo/pull/123",
            "auto_commit_enabled": True,
        }

    def test_from_dict(self):
        """Test creation from dictionary"""
        data = {
            "branch_name": "vibe-456",
            "session_start_time": "2024-01-01T11:00:00",
            "last_commit_time": None,
            "pr_url": None,
            "auto_commit_enabled": False,
        }

        state = PersistedSessionState.from_dict(data)

        assert state.branch_name == "vibe-456"
        assert state.session_start_time == "2024-01-01T11:00:00"
        assert state.last_commit_time is None
        assert state.pr_url is None
        assert state.auto_commit_enabled is False


class TestSessionPersistence:
    """Test the SessionPersistence class"""

    def test_save_and_load_session(self, tmp_path):
        """Test saving and loading session state"""
        # Create a git repo
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        persistence = SessionPersistence(tmp_path)
        state = PersistedSessionState(
            branch_name=BranchName("vibe-789"),
            session_start_time=datetime.now().isoformat(),
        )

        # Save session
        persistence.save_session(state)

        # Load session
        loaded = persistence.load_session()

        assert loaded is not None
        assert loaded.branch_name == state.branch_name
        assert loaded.session_start_time == state.session_start_time

    def test_load_nonexistent_session(self, tmp_path):
        """Test loading when no session exists"""
        # Create a git repo
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        persistence = SessionPersistence(tmp_path)
        result = persistence.load_session()

        assert result is None

    def test_load_corrupted_session(self, tmp_path):
        """Test loading corrupted session file"""
        # Create a git repo
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        persistence = SessionPersistence(tmp_path)

        # Write corrupted JSON
        persistence.state_file.write_text("not valid json")

        result = persistence.load_session()

        assert result is None
        assert not persistence.state_file.exists()

    def test_delete_session(self, tmp_path):
        """Test deleting session"""
        # Create a git repo
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        persistence = SessionPersistence(tmp_path)
        state = PersistedSessionState(
            branch_name=BranchName("vibe-delete"),
            session_start_time=datetime.now().isoformat(),
        )

        # Save and then delete
        persistence.save_session(state)
        assert persistence.has_session()

        persistence.delete_session()

        assert not persistence.has_session()
        assert persistence.load_session() is None

    def test_has_session(self, tmp_path):
        """Test checking if session exists"""
        # Create a git repo
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        persistence = SessionPersistence(tmp_path)

        assert not persistence.has_session()

        # Create session
        state = PersistedSessionState(
            branch_name=BranchName("vibe-exist"),
            session_start_time=datetime.now().isoformat(),
        )
        persistence.save_session(state)

        assert persistence.has_session()

    def test_session_age(self, tmp_path):
        """Test getting session age"""
        # Create a git repo
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        persistence = SessionPersistence(tmp_path)

        # No session
        assert persistence.get_session_age_seconds() is None

        # Create session with known timestamp
        past_time = datetime.now() - timedelta(hours=2)
        state = PersistedSessionState(
            branch_name=BranchName("vibe-age"),
            session_start_time=past_time.isoformat(),
        )
        persistence.save_session(state)

        age = persistence.get_session_age_seconds()
        assert age is not None
        assert 7190 < age < 7210  # About 2 hours (allowing some variance)

    def test_is_session_stale(self, tmp_path):
        """Test checking if session is stale"""
        # Create a git repo
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        persistence = SessionPersistence(tmp_path)

        # No session - not stale
        assert not persistence.is_session_stale()

        # Fresh session
        state = PersistedSessionState(
            branch_name=BranchName("vibe-fresh"),
            session_start_time=datetime.now().isoformat(),
        )
        persistence.save_session(state)

        assert not persistence.is_session_stale(max_age_hours=24)

        # Old session
        old_time = datetime.now() - timedelta(hours=25)
        state.session_start_time = old_time.isoformat()
        persistence.save_session(state)

        assert persistence.is_session_stale(max_age_hours=24)
        assert not persistence.is_session_stale(max_age_hours=48)

    def test_append_event(self, tmp_path):
        """Test appending events to the log"""
        # Create a git repo
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        persistence = SessionPersistence(tmp_path)

        # Append some events
        persistence.append_event({"event": "session_started", "branch": "vibe-123"})
        persistence.append_event({"event": "commit_made", "hash": "abc123"})

        # Read events back
        events = persistence.events_file.read_text().strip().split("\n")
        assert len(events) == 2

        event1 = json.loads(events[0])
        assert event1["event"] == "session_started"
        assert event1["branch"] == "vibe-123"

        event2 = json.loads(events[1])
        assert event2["event"] == "commit_made"
        assert event2["hash"] == "abc123"
