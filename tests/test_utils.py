"""Test utilities for vibe-git tests"""

from vibe_git.main import IdleState, VibingState, session


def reset_session():
    """Reset the session to idle state for testing"""
    # Stop any active file watcher
    if isinstance(session.state, VibingState):
        if session.state.observer:
            session.state.observer.stop()
            session.state.observer.join(timeout=1)
        if session.state.commit_event:
            session.state.commit_event.set()

    # Reset to idle state
    session.transition_to(IdleState())


def is_vibing() -> bool:
    """Check if currently vibing"""
    return isinstance(session.state, VibingState)


def get_current_branch() -> str | None:
    """Get current vibe branch if vibing"""
    if isinstance(session.state, VibingState):
        return session.state.branch_name
    return None
