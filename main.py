#!/usr/bin/env python3
"""
vibe-git MCP Server - Friction-free git workflows for vibe coding

Enables developers to focus on code while git operations happen automatically.
"""

import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from threading import Event, Thread

from fastmcp import FastMCP
from pydantic import BaseModel
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


@dataclass
class VibeSession:
    """Represents the current vibe session state"""

    branch_name: str | None = None
    is_vibing: bool = False
    observer: Observer | None = None
    commit_event: Event | None = None


class CommitMessage(BaseModel):
    """Schema for stop_vibing arguments"""

    commit_message: str


# Global session state
session = VibeSession()

# Create FastMCP app
mcp = FastMCP("vibe-git")


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


class VibeFileHandler(FileSystemEventHandler):
    """Handles file system events for auto-committing"""

    def __init__(self, repo_path: Path, commit_event: Event):
        super().__init__()
        self.repo_path = repo_path
        self.commit_event = commit_event
        self.last_commit_time = 0
        self.min_commit_interval = 1  # Minimum 1 second between commits

    def should_ignore_path(self, path: str) -> bool:
        """Check if path should be ignored based on git and common patterns"""
        path_obj = Path(path)

        # Ignore git directory and common temp files
        ignore_patterns = [
            ".git",
            "__pycache__",
            ".pytest_cache",
            ".venv",
            "node_modules",
            ".DS_Store",
            "*.pyc",
            "*.pyo",
            "*.swp",
            "*.tmp",
            ".coverage",
        ]

        for pattern in ignore_patterns:
            if pattern.startswith("*"):
                if path_obj.name.endswith(pattern[1:]):
                    return True
            elif pattern in path_obj.parts:
                return True

        return False

    def on_any_event(self, event):
        """Handle any file system event"""
        if event.is_directory:
            return

        if self.should_ignore_path(event.src_path):
            return

        # Rate limit commits to avoid spam
        current_time = time.time()
        if current_time - self.last_commit_time < self.min_commit_interval:
            return

        self.last_commit_time = current_time
        self.commit_event.set()


def auto_commit_worker():
    """Worker thread that commits changes when signaled"""
    repo_path = find_git_repo()

    while session.is_vibing and session.commit_event:
        try:
            # Wait for commit signal
            if session.commit_event.wait(timeout=1):
                session.commit_event.clear()

                # Check for actual changes before committing
                success, output = run_git_command(["status", "--porcelain"], repo_path)
                if success and output.strip():
                    # Add all changes
                    run_git_command(["add", "."], repo_path)

                    # Commit with timestamp
                    timestamp = int(time.time())
                    commit_msg = f"Auto-commit {timestamp}"
                    run_git_command(["commit", "-m", commit_msg], repo_path)

        except Exception:
            # Continue on any errors
            time.sleep(0.1)


def _start_vibing_impl() -> str:
    """Core implementation of start_vibing functionality."""
    global session

    if session.is_vibing:
        return "Already vibing! Session is active and auto-committing changes."

    try:
        repo_path = find_git_repo()

        # Generate branch name
        timestamp = int(time.time())
        branch_name = f"vibe-{timestamp}"

        # Check current branch
        success, current_branch = run_git_command(
            ["branch", "--show-current"], repo_path
        )
        if success and current_branch.startswith("vibe-"):
            # We're already on a vibe branch - reuse it instead of creating a new one
            session.branch_name = current_branch
        if success and current_branch.strip().startswith("vibe-"):
            # We're already on a vibe branch - reuse it instead of creating a new one
            session.branch_name = current_branch.strip()
            session.is_vibing = True

            # Set up file watcher
            session.commit_event = Event()
            session.observer = Observer()
            event_handler = VibeFileHandler(repo_path, session.commit_event)
            session.observer.schedule(
                event_handler, path=str(repo_path), recursive=True
            )
            session.observer.start()

            # Start commit worker thread
            commit_thread = Thread(target=auto_commit_worker, daemon=True)
            commit_thread.start()

            return f"🚀 Started vibing! Reusing existing vibe branch '{current_branch}' and auto-committing changes on file modifications."

        # Ensure we're on main branch
        success, _ = run_git_command(["checkout", "main"], repo_path)
        if not success:
            # Try master if main doesn't exist
            success, _ = run_git_command(["checkout", "master"], repo_path)
            if not success:
                return "❌ Error: Could not checkout main/master branch. Try manually switching to main first."

            return f"🚀 Started vibing! Reusing existing vibe branch '{current_branch.strip()}' and auto-committing changes on file modifications."

        # Check for uncommitted changes
        status_success, status_output = run_git_command(
            ["status", "--porcelain"], repo_path
        )
        has_changes = status_success and status_output.strip()

        if has_changes:
            # Get current branch for context
            _, current = run_git_command(["branch", "--show-current"], repo_path)
            return (
                f"⚠️ Uncommitted changes detected on branch '{current.strip()}'!\n\n"
                "Choose one of these functions:\n"
                "• commit_and_vibe() - Commit changes as 'WIP' then start from main\n"
                "• stash_and_vibe() - Stash changes then start from main\n"
                "• vibe_from_here() - Start vibing from current branch with changes\n"
            )

        # Ensure we're on main branch and pull latest
        main_success, _ = run_git_command(["checkout", "main"], repo_path)
        if main_success:
            main_branch = "main"
        else:
            # Try master if main doesn't exist
            master_success, _ = run_git_command(["checkout", "master"], repo_path)
            if master_success:
                main_branch = "master"
            else:
                return "❌ Error: Could not checkout main/master branch. Try manually switching to main first."

        # Pull latest changes from origin
        run_git_command(["pull", "origin", main_branch], repo_path)

        # Create and checkout new branch
        success, output = run_git_command(["checkout", "-b", branch_name], repo_path)
        if not success:
            return f"❌ Error creating branch: {output}"

        # Start auto-commit watcher
        session.branch_name = branch_name
        session.is_vibing = True

        # Set up file watcher
        session.commit_event = Event()
        session.observer = Observer()
        event_handler = VibeFileHandler(repo_path, session.commit_event)
        session.observer.schedule(event_handler, path=str(repo_path), recursive=True)
        session.observer.start()

        # Start commit worker thread
        commit_thread = Thread(target=auto_commit_worker, daemon=True)
        commit_thread.start()

        return f"🚀 Started vibing! Created branch '{branch_name}' from latest {main_branch} and auto-committing changes on file modifications."

    except Exception as e:
        return f"❌ Error starting vibe session: {e}"


@mcp.tool()
def start_vibing() -> str:
    """🚀 CALL THIS FIRST before making any code changes! Creates a new git branch and starts auto-committing all file changes every second. Safe to call multiple times - will not create duplicate sessions."""
    return _start_vibing_impl()


@mcp.tool()
def stop_vibing(commit_message: str) -> str:
    """🏁 Call this ONLY when the user explicitly says to stop or asks you to stop the session. Squashes all auto-commits into a single commit with your message, rebases onto latest main, and creates a PR. Do NOT call this automatically - wait for user confirmation before stopping. Safe to call even if not vibing.

    The commit_message should be a comprehensive description that will be used for:
    - The squashed commit message
    - The PR title (first line)
    - The PR body (full message)

    Format suggestion:
    "Short summary of changes

    Detailed description of what was changed, why it was changed,
    and any important implementation details or decisions."""
    global session

    if not session.is_vibing:
        return "Not currently vibing. You can start a vibe session with start_vibing()."

    try:
        repo_path = find_git_repo()
        branch_name = session.branch_name
        # commit_message is now passed directly as parameter

        # Stop the file watcher
        if session.observer:
            session.observer.stop()
            session.observer.join(timeout=2)
        if session.commit_event:
            session.commit_event.set()  # Wake up commit worker to exit

        # Squash commits using interactive rebase
        # First, find the commit where we branched from main
        success, output = run_git_command(["merge-base", "main", "HEAD"], repo_path)
        if not success:
            # Try master
            success, output = run_git_command(
                ["merge-base", "master", "HEAD"], repo_path
            )
            if not success:
                return f"❌ Error finding branch point: {output}"

        base_commit = output.strip()

        # Count commits to squash
        success, output = run_git_command(
            ["rev-list", "--count", f"{base_commit}..HEAD"], repo_path
        )
        if success and int(output.strip()) > 1:
            # Reset to base commit and create single commit
            success, _ = run_git_command(["reset", "--soft", base_commit], repo_path)
            if success:
                run_git_command(["commit", "-m", commit_message], repo_path)

        # Checkout main and pull latest
        run_git_command(["checkout", "main"], repo_path)
        run_git_command(["pull", "origin", "main"], repo_path)

        # Rebase our branch
        run_git_command(["checkout", branch_name], repo_path)
        success, output = run_git_command(["rebase", "main"], repo_path)
        if not success:
            return f"❌ Error rebasing: {output}"

        # Push branch
        success, output = run_git_command(
            ["push", "-u", "origin", branch_name], repo_path
        )
        if not success:
            return f"❌ Error pushing branch: {output}"

        # Extract PR title from first line of commit message
        lines = commit_message.strip().split("\n")
        pr_title = lines[0] if lines else commit_message
        pr_body = commit_message  # Use full message as body

        # Try to create PR using GitHub CLI
        success, output = run_git_command(
            ["gh", "pr", "create", "--title", pr_title, "--body", pr_body], repo_path
        )

        pr_info = ""
        if success:
            pr_info = f"\n📋 Created PR: {output}"

        # Reset session state
        session.is_vibing = False
        session.branch_name = None
        session.observer = None
        session.commit_event = None

        return f"🏁 Stopped vibing! Squashed commits into: '{commit_message}', rebased on main, and pushed to origin.{pr_info}"

    except Exception as e:
        # Reset session state on error
        session.is_vibing = False
        session.branch_name = None
        if session.observer:
            session.observer.stop()
        session.observer = None
        session.commit_event = None
        return f"❌ Error stopping vibe session: {e}"


@mcp.tool()
def stash_and_vibe() -> str:
    """📦 Stash uncommitted changes and start a new vibe session from main. Your changes will be saved and can be restored later with 'git stash pop'."""
    try:
        repo_path = find_git_repo()

        # Check for changes to stash
        status_success, status_output = run_git_command(
            ["status", "--porcelain"], repo_path
        )
        if not (status_success and status_output.strip()):
            return "No changes to stash. Proceeding to start vibe session..."

        # Stash changes
        success, output = run_git_command(
            ["stash", "push", "-m", "Pre-vibe stash"], repo_path
        )
        if not success:
            return f"❌ Error stashing changes: {output}"

        # Now start vibing
        return (
            _start_vibing_impl()
            + "\n\n💡 Your changes are stashed. Run 'git stash pop' after vibing to restore them."
        )

    except Exception as e:
        return f"❌ Error: {e}"


@mcp.tool()
def commit_and_vibe() -> str:
    """💾 Commit all uncommitted changes as 'WIP' and start a new vibe session from main."""
    try:
        repo_path = find_git_repo()

        # Check for changes
        status_success, status_output = run_git_command(
            ["status", "--porcelain"], repo_path
        )
        if not (status_success and status_output.strip()):
            return "No changes to commit. Proceeding to start vibe session..."

        # Add all changes
        success, _ = run_git_command(["add", "."], repo_path)
        if not success:
            return "❌ Error adding changes. Check if files are ignored by .gitignore"

        # Commit as WIP
        success, output = run_git_command(
            ["commit", "-m", "WIP: Pre-vibe commit"], repo_path
        )
        if not success:
            return f"❌ Error committing changes: {output}"

        # Now start vibing
        return (
            _start_vibing_impl()
            + "\n\n✅ Your changes were committed as 'WIP: Pre-vibe commit'"
        )

    except Exception as e:
        return f"❌ Error: {e}"


@mcp.tool()
def vibe_from_here() -> str:
    """🌿 Start vibing from the current branch with all existing changes. Any uncommitted changes will be auto-committed as part of the vibe session."""
    global session

    if session.is_vibing:
        return "Already vibing! Session is active and auto-committing changes."

    try:
        repo_path = find_git_repo()

        # Get current branch
        success, current_branch = run_git_command(
            ["branch", "--show-current"], repo_path
        )
        if not success:
            return "❌ Error: Could not determine current branch"
        current_branch = current_branch.strip()

        # Generate vibe branch name if not already on one
        if not current_branch.startswith("vibe-"):
            timestamp = int(time.time())
            branch_name = f"vibe-{timestamp}"

            # Create new branch from current position
            success, output = run_git_command(
                ["checkout", "-b", branch_name], repo_path
            )

            if not success:
                return f"❌ Error creating branch: {output}"
        else:
            branch_name = current_branch

        # Start auto-commit watcher
        session.branch_name = branch_name
        session.is_vibing = True

        # Set up file watcher
        session.commit_event = Event()
        session.observer = Observer()
        event_handler = VibeFileHandler(repo_path, session.commit_event)
        session.observer.schedule(event_handler, path=str(repo_path), recursive=True)
        session.observer.start()

        # Start commit worker thread
        commit_thread = Thread(target=auto_commit_worker, daemon=True)
        commit_thread.start()

        # Check for uncommitted changes
        status_success, status_output = run_git_command(
            ["status", "--porcelain"], repo_path
        )
        has_changes = status_success and status_output.strip()

        if has_changes:
            # Trigger immediate commit of existing changes
            session.commit_event.set()
            return f"🚀 Started vibing on branch '{branch_name}'! Existing uncommitted changes will be auto-committed shortly."
        else:
            return f"🚀 Started vibing on branch '{branch_name}'! Auto-committing future changes."

    except Exception as e:
        return f"❌ Error starting vibe session: {e}"


@mcp.tool()
def vibe_status() -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle. Use this to understand the current state."""
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


def signal_handler(sig, frame):
    """Handle SIGINT/SIGTERM gracefully"""
    global session
    if session.observer:
        session.observer.stop()
    session.is_vibing = False
    sys.exit(0)


def main():
    """Main entry point for the MCP server"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run the MCP server
    mcp.run()


if __name__ == "__main__":
    main()
