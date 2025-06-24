"""State types for the vibe-git state machine"""

from dataclasses import dataclass
from threading import Event

from watchdog.observers import Observer

from .type_utils import BranchName


# State types for type-safe state machine
@dataclass(frozen=True)
class IdleState:
    """No active vibe session"""

    pass


@dataclass(frozen=True)
class VibingState:
    """Active vibe session"""

    branch_name: BranchName
    observer: Observer
    commit_event: Event


@dataclass(frozen=True)
class DirtyState:
    """Repository has uncommitted changes"""

    branch_name: str
    changes: str


SessionState = IdleState | VibingState | DirtyState


@dataclass
class VibeSession:
    """Type-safe vibe session with state tracking"""

    state: SessionState = IdleState()

    def transition_to(self, new_state: SessionState) -> None:
        """Type-safe state transition"""
        self.state = new_state