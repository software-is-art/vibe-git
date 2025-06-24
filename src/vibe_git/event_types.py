"""Event types for type-safe event handling"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .state_types import SessionState
from .type_utils import BranchName, CommitHash, CommitMessage


@dataclass(frozen=True)
class CommitEvent:
    """Event triggered when files need to be committed"""
    
    timestamp: datetime
    files_changed: list[Path]
    branch_name: BranchName
    
    @property
    def has_changes(self) -> bool:
        """Check if there are any files to commit"""
        return bool(self.files_changed)


@dataclass(frozen=True)
class StateTransitionEvent:
    """Event for tracking state machine transitions"""
    
    from_state: type["SessionState"]
    to_state: type["SessionState"]
    timestamp: datetime
    reason: str | None = None
    
    @property
    def state_changed(self) -> bool:
        """Check if the state actually changed"""
        return self.from_state != self.to_state


@dataclass(frozen=True) 
class SessionStartEvent:
    """Event when a vibe session starts"""
    
    branch_name: BranchName
    timestamp: datetime
    resumed: bool = False
    previous_branch: BranchName | None = None


@dataclass(frozen=True)
class SessionStopEvent:
    """Event when a vibe session stops"""
    
    branch_name: BranchName
    timestamp: datetime
    commit_count: int
    pr_created: bool
    commit_message: CommitMessage | None = None
    
    
@dataclass(frozen=True)
class GitOperationEvent:
    """Event for tracking git operations"""
    
    operation: str  # e.g., "checkout", "commit", "push"
    args: list[str]
    success: bool
    output: str
    timestamp: datetime
    
    @property
    def failed(self) -> bool:
        """Check if the operation failed"""
        return not self.success


@dataclass(frozen=True)
class FileWatchEvent:
    """Event from file system watcher"""
    
    path: Path
    event_type: str  # e.g., "created", "modified", "deleted"
    timestamp: datetime
    ignored: bool = False