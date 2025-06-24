"""State persistence for vibe-git sessions

This module handles saving and loading vibe session state to enable
recovery after MCP restarts or crashes.
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime

from .type_utils import BranchName, GitPath


@dataclass
class PersistedSessionState:
    """Session state that persists between MCP restarts"""

    branch_name: BranchName
    session_start_time: str  # ISO format timestamp
    last_commit_time: str | None = None  # ISO format timestamp
    pr_url: str | None = None
    auto_commit_enabled: bool = True

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "PersistedSessionState":
        """Create from dictionary"""
        return cls(**data)


class SessionPersistence:
    """Handles reading and writing session state"""

    def __init__(self, repo_path: GitPath):
        self.repo_path = repo_path
        self.state_file = repo_path / ".git" / "vibe-session.json"
        self.events_file = repo_path / ".git" / "vibe-events.jsonl"

    def save_session(self, state: PersistedSessionState) -> None:
        """Save session state to disk"""
        self.state_file.write_text(json.dumps(state.to_dict(), indent=2))

        # Also append to events log
        self.append_event(
            {
                "event": "session_saved",
                "timestamp": datetime.now().isoformat(),
                "state": state.to_dict(),
            }
        )

    def load_session(self) -> PersistedSessionState | None:
        """Load session state from disk"""
        if not self.state_file.exists():
            return None

        try:
            data = json.loads(self.state_file.read_text())
            return PersistedSessionState.from_dict(data)
        except (json.JSONDecodeError, KeyError, TypeError):
            # Corrupted state file - remove it
            self.state_file.unlink(missing_ok=True)
            return None

    def delete_session(self) -> None:
        """Delete session state"""
        self.state_file.unlink(missing_ok=True)

        # Append final event
        self.append_event(
            {"event": "session_ended", "timestamp": datetime.now().isoformat()}
        )

    def append_event(self, event: dict) -> None:
        """Append event to the events log"""
        with self.events_file.open("a") as f:
            f.write(json.dumps(event) + "\n")

    def has_session(self) -> bool:
        """Check if a session exists"""
        return self.state_file.exists()

    def get_session_age_seconds(self) -> float | None:
        """Get age of session in seconds"""
        state = self.load_session()
        if not state:
            return None

        try:
            start_time = datetime.fromisoformat(state.session_start_time)
            age = (datetime.now() - start_time).total_seconds()
            return age
        except (ValueError, TypeError):
            return None

    def is_session_stale(self, max_age_hours: int = 24) -> bool:
        """Check if session is too old"""
        age_seconds = self.get_session_age_seconds()
        if age_seconds is None:
            return False

        return age_seconds > (max_age_hours * 3600)
