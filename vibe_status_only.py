#!/usr/bin/env python3
"""
Minimal version of vibe status logic for focused mutation testing.
"""

import subprocess
from pathlib import Path


class VibeSession:
    """Represents the current vibe session state"""

    def __init__(self):
        self.branch_name = None
        self.is_vibing = False
        self.observer = None
        self.commit_event = None


def find_git_repo() -> Path:
    """Find the git repository root"""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    raise RuntimeError("Not in a git repository")


def run_git_command(args: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    """Run a git command and return (success, output)"""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd or find_git_repo(),
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0, result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return False, str(e)


def vibe_status(session: VibeSession) -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle."""
    try:
        repo_path = find_git_repo()

        # Get current branch
        success, current_branch = run_git_command(
            ["branch", "--show-current"], repo_path
        )
        if not success:
            return "⚪ NOT INITIALIZED: Could not determine current branch"
        current_branch = current_branch.strip()  # Remove any whitespace

        # Check if we have an active vibe session
        if session.is_vibing and session.branch_name:
            if current_branch == session.branch_name:
                return f"🟢 VIBING: Active session on branch '{session.branch_name}' - auto-committing changes on file modifications"
            else:
                # Session state is inconsistent, reset it
                session.is_vibing = False
                session.branch_name = None

        # Check if we're on a vibe branch but session is idle (e.g., after MCP restart)
        if current_branch.startswith("vibe-") and not session.is_vibing:
            return f"🟡 VIBE BRANCH DETECTED: On branch '{current_branch}' but session is idle. Call start_vibing() to resume or vibe_from_here() to restart watching."

        return "🔵 IDLE: Ready to start vibing. Call start_vibing() to begin!"

    except Exception as e:
        return f"⚪ NOT INITIALIZED: Error checking repository status: {e}"
