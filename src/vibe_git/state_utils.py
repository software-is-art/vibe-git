"""State machine utilities with type safety"""

from typing import assert_never

from plum import dispatch

from .state_types import DirtyState, IdleState, SessionState, VibingState


def get_state_name(state: SessionState) -> str:
    """Get human-readable name for a state with exhaustiveness checking"""
    if isinstance(state, IdleState):
        return "idle"
    elif isinstance(state, VibingState):
        return "vibing"
    elif isinstance(state, DirtyState):
        return "dirty"
    else:
        # This ensures we handle all state types
        assert_never(state)


@dispatch
def can_transition_to(from_state: IdleState, to_state: SessionState) -> bool:
    """Check if transition from IdleState is valid"""
    # From idle, we can go to vibing or dirty
    return isinstance(to_state, VibingState | DirtyState)


@dispatch
def can_transition_to(from_state: VibingState, to_state: SessionState) -> bool:  # noqa: F811
    """Check if transition from VibingState is valid"""
    # From vibing, we can only go to idle (when stopping)
    return isinstance(to_state, IdleState)


@dispatch
def can_transition_to(from_state: DirtyState, to_state: SessionState) -> bool:  # noqa: F811
    """Check if transition from DirtyState is valid"""
    # From dirty, we can go to idle (after resolving) or vibing
    return isinstance(to_state, IdleState | VibingState)


def validate_state_transition(from_state: SessionState, to_state: SessionState) -> None:
    """Validate a state transition, raising if invalid"""
    if not can_transition_to(from_state, to_state):
        from_name = get_state_name(from_state)
        to_name = get_state_name(to_state)
        raise ValueError(f"Invalid state transition from {from_name} to {to_name}")


def get_allowed_transitions(state: SessionState) -> list[type[SessionState]]:
    """Get list of allowed state types from current state"""
    if isinstance(state, IdleState):
        return [VibingState, DirtyState]
    elif isinstance(state, VibingState):
        return [IdleState]
    elif isinstance(state, DirtyState):
        return [IdleState, VibingState]
    else:
        assert_never(state)
