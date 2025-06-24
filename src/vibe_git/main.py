#!/usr/bin/env python3
"""
vibe-git MCP Server - Friction-free git workflows for vibe coding

Enables developers to focus on code while git operations happen automatically.
Enhanced with beartype for runtime type safety and plum for clean dispatch patterns.
"""

import signal
import subprocess
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from threading import Event, Thread
from typing import Literal, NewType, TypeAlias

from beartype import beartype
from beartype.typing import Annotated
from beartype.vale import Is
from fastmcp import FastMCP
from plum import dispatch
from pydantic import BaseModel
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# Type definitions with beartype validation
GitPath = Annotated[Path, Is[lambda p: (p / ".git").exists()]]
BranchName = NewType("BranchName", str)
CommitHash = NewType("CommitHash", str)
PRTitle = NewType("PRTitle", str)
PRBody = NewType("PRBody", str)
PRUrl = NewType("PRUrl", str)
CommitTimestamp = NewType("CommitTimestamp", int)
NonEmptyString = Annotated[str, Is[lambda s: len(s.strip()) > 0]]

CommandResult: TypeAlias = tuple[bool, str]

# Result types for rich return values
@dataclass
class VibeStartResult:
    """Result of starting a vibe session"""
    success: bool
    branch_name: BranchName | None
    message: str
    warnings: list[str] = None
    
    def __str__(self) -> str:
        if self.warnings:
            return f"{self.message}\n\n" + "\n".join(f"⚠️ {w}" for w in self.warnings)
        return self.message

@dataclass  
class VibeStopResult:
    """Result of stopping a vibe session"""
    success: bool
    pr_url: PRUrl | None
    message: str
    squashed_commits: int = 0
    had_conflicts: bool = False
    warnings: list[str] = None
    
    def __str__(self) -> str:
        parts = [self.message]
        if self.pr_url:
            parts.append(f"\n📋 Created PR: {self.pr_url}")
        if self.warnings:
            parts.extend(f"\n⚠️ {w}" for w in self.warnings)
        return "".join(parts)

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
    
    @beartype
    def transition_to(self, new_state: SessionState) -> None:
        """Type-safe state transition"""
        self.state = new_state


class CommitMessage(BaseModel):
    """Schema for stop_vibing arguments"""
    commit_message: str


# Global session state
session = VibeSession()

# Create FastMCP app
mcp = FastMCP("vibe-git")


@beartype
def find_git_repo() -> GitPath:
    """Find the git repository root with type safety"""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".git").exists():
            return GitPath(current)
        current = current.parent
    raise RuntimeError("Not in a git repository")


@dispatch
@beartype
def run_command(args: list[str], cwd: Path | None = None) -> CommandResult:
    """Run any command with type-safe return"""
    try:
        result = subprocess.run(
            args,
            cwd=cwd or find_git_repo(),
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0, result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return False, str(e)


@dispatch
@beartype
def run_command(command: str, cwd: Path | None = None) -> CommandResult:
    """Overload for single string commands"""
    return run_command(command.split(), cwd)


@beartype
def run_git_command(args: list[str], cwd: Path | None = None) -> CommandResult:
    """Run a git command with type safety"""
    return run_command(["git"] + args, cwd)


@beartype
def get_current_branch(repo_path: GitPath) -> BranchName | None:
    """Get current branch name with type safety"""
    success, output = run_git_command(["branch", "--show-current"], repo_path)
    if success and output:
        return BranchName(output.strip())
    # Handle detached HEAD state
    if not success and output.strip().startswith("vibe-"):
        return BranchName(output.strip())
    return None


@beartype
def has_uncommitted_changes(repo_path: GitPath) -> tuple[bool, str]:
    """Check for uncommitted changes with details"""
    success, output = run_git_command(["status", "--porcelain"], repo_path)
    has_changes = success and bool(output.strip())
    return has_changes, output.strip() if has_changes else ""


@beartype
def is_vibe_branch(branch: str) -> bool:
    """Check if a branch name is a vibe branch"""
    return branch.startswith("vibe-")


@beartype
def generate_timestamp() -> CommitTimestamp:
    """Generate commit timestamp with validation"""
    return CommitTimestamp(int(time.time()))


@contextmanager
def atomic_state_transition(session: VibeSession):
    """Ensure state transitions are atomic"""
    original_state = session.state
    try:
        yield
    except Exception:
        session.state = original_state
        raise


class VibeFileHandler(FileSystemEventHandler):
    """Handles file system events for auto-committing"""

    @beartype
    def __init__(self, repo_path: GitPath, commit_event: Event):
        super().__init__()
        self.repo_path = repo_path
        self.commit_event = commit_event
        self.last_commit_time = 0.0
        self.min_commit_interval = 0.0

    @beartype
    def should_ignore_path(self, path: str) -> bool:
        """Check if path should be ignored based on git's ignore rules"""
        path_obj = Path(path)
        if ".git" in path_obj.parts:
            return True

        # Use git check-ignore to determine if file should be ignored
        try:
            relative_path = path_obj.relative_to(self.repo_path)
            success, _ = run_git_command(
                ["check-ignore", str(relative_path)], self.repo_path
            )
            return success  # git check-ignore returns 0 if file is ignored
        except ValueError:
            return True  # Path not relative to repo

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


@beartype
def auto_commit_worker() -> None:
    """Worker thread that commits changes when signaled"""
    repo_path = find_git_repo()

    while isinstance(session.state, VibingState):
        try:
            # Wait for commit signal
            if session.state.commit_event.wait(timeout=1):
                session.state.commit_event.clear()

                # Check for actual changes before committing
                has_changes, _ = has_uncommitted_changes(repo_path)

                if has_changes:
                    # Add all changes
                    run_git_command(["add", "."], repo_path)

                    # Commit with timestamp, bypassing hooks during vibe session
                    timestamp = generate_timestamp()
                    commit_msg = f"Auto-commit {timestamp}"
                    run_git_command(
                        ["commit", "-m", commit_msg, "--no-verify"], repo_path
                    )

        except Exception as e:
            print(f"Auto-commit worker error: {e}", file=sys.stderr)
            time.sleep(0.1)


@beartype
def ensure_on_main_branch(repo_path: GitPath) -> Literal["main", "master"] | None:
    """Ensure we're on main/master branch"""
    success, _ = run_git_command(["checkout", "main"], repo_path)
    if success:
        return "main"
    
    success, _ = run_git_command(["checkout", "master"], repo_path)
    if success:
        return "master"
    
    return None


@beartype
def start_file_watcher(repo_path: GitPath, branch_name: BranchName) -> VibingState:
    """Start file watching for auto-commit"""
    commit_event = Event()
    observer = Observer()
    event_handler = VibeFileHandler(repo_path, commit_event)
    observer.schedule(event_handler, path=str(repo_path), recursive=True)
    observer.start()
    
    # Start commit worker
    commit_thread = Thread(target=auto_commit_worker, daemon=True)
    commit_thread.start()
    
    return VibingState(
        branch_name=branch_name,
        observer=observer,
        commit_event=commit_event
    )


# Dispatch implementations for different repository states
@dispatch
@beartype
def start_vibing_from_state(state: IdleState, repo_path: GitPath) -> VibeStartResult:
    """Start vibing from idle state"""
    # Check current branch first
    current = get_current_branch(repo_path)
    
    # Check if we're already on a vibe branch (e.g., after MCP restart)
    if current and is_vibe_branch(current):
        # Reuse existing vibe branch
        new_state = start_file_watcher(repo_path, current)
        with atomic_state_transition(session):
            session.transition_to(new_state)
        
        return VibeStartResult(
            success=True,
            branch_name=current,
            message=f"🚀 Started vibing! Reusing existing vibe branch '{current}' and auto-committing changes on file modifications."
        )
    
    # Check for uncommitted changes
    has_changes, changes = has_uncommitted_changes(repo_path)
    
    if has_changes:
        current_branch = current or "unknown"
        with atomic_state_transition(session):
            session.transition_to(DirtyState(branch_name=current_branch, changes=changes))
        
        return VibeStartResult(
            success=False,
            branch_name=None,
            message=(
                f"⚠️ Uncommitted changes detected on branch '{current_branch}'!\n\n"
                "Choose one of these functions:\n"
                "• commit_and_vibe() - Commit changes as 'WIP' then start from main\n"
                "• stash_and_vibe() - Stash changes then start from main\n"
                "• vibe_from_here() - Start vibing from current branch with changes\n"
            )
        )
    
    # Ensure on main branch
    main_branch = ensure_on_main_branch(repo_path)
    if not main_branch:
        return VibeStartResult(
            success=False,
            branch_name=None,
            message="❌ Error: Could not checkout main/master branch. Try manually switching to main first."
        )
    
    # Pull latest changes
    run_git_command(["pull", "origin", main_branch], repo_path)
    
    # Create new vibe branch
    timestamp = generate_timestamp()
    branch_name = BranchName(f"vibe-{timestamp}")
    
    success, output = run_git_command(["checkout", "-b", branch_name], repo_path)
    if not success:
        return VibeStartResult(
            success=False,
            branch_name=None,
            message=f"❌ Error creating branch: {output}"
        )
    
    # Start file watching
    new_state = start_file_watcher(repo_path, branch_name)
    with atomic_state_transition(session):
        session.transition_to(new_state)
    
    return VibeStartResult(
        success=True,
        branch_name=branch_name,
        message=f"🚀 Started vibing! Created branch '{branch_name}' from latest {main_branch} and auto-committing changes on file modifications."
    )


@dispatch
@beartype
def start_vibing_from_state(state: VibingState, repo_path: GitPath) -> VibeStartResult:
    """Already vibing - return status"""
    return VibeStartResult(
        success=True,
        branch_name=state.branch_name,
        message="Already vibing! Session is active and auto-committing changes."
    )


@dispatch
@beartype
def start_vibing_from_state(state: DirtyState, repo_path: GitPath) -> VibeStartResult:
    """Can't start from dirty state - return instructions"""
    return VibeStartResult(
        success=False,
        branch_name=None,
        message=(
            f"⚠️ Uncommitted changes still detected on branch '{state.branch_name}'!\n\n"
            "Choose one of these functions:\n"
            "• commit_and_vibe() - Commit changes as 'WIP' then start from main\n"
            "• stash_and_vibe() - Stash changes then start from main\n"
            "• vibe_from_here() - Start vibing from current branch with changes\n"
        )
    )


@beartype
def parse_commit_message(message: str) -> tuple[PRTitle, PRBody]:
    """Parse commit message into title and body"""
    lines = message.strip().split("\n")
    title = PRTitle(lines[0] if lines else message)
    body = PRBody(message)
    return title, body


@beartype
def run_git_with_hook_retry(
    args: list[str], 
    repo_path: GitPath,
    max_retries: int = 2
) -> CommandResult:
    """Run git command with automatic retry for hook failures"""
    for attempt in range(max_retries):
        success, output = run_git_command(args, repo_path)
        if success or "hook" not in output.lower():
            return success, output
        # Wait for hooks to complete
        time.sleep(1)
    return False, f"Failed after {max_retries} attempts: {output}"


@mcp.tool()
@beartype
def start_vibing() -> str:
    """🚀 CALL THIS FIRST before making any code changes! Creates a new git branch and starts auto-committing all file changes every second. Safe to call multiple times - will not create duplicate sessions."""
    try:
        repo_path = find_git_repo()
        result = start_vibing_from_state(session.state, repo_path)
        return str(result)
    except Exception as e:
        return f"❌ Error starting vibe session: {e}"


@mcp.tool()
@beartype
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
    
    if not isinstance(session.state, VibingState):
        return "Not currently vibing. You can start a vibe session with start_vibing()."
    
    try:
        repo_path = find_git_repo()
        branch_name = session.state.branch_name
        warnings = []
        
        # NOTE: We keep the file watcher running during stop_vibing
        # This ensures any hook-induced changes get auto-committed before we finish
        
        # Find base commit
        success, base_commit = run_git_command(["merge-base", "main", "HEAD"], repo_path)
        if not success:
            success, base_commit = run_git_command(["merge-base", "master", "HEAD"], repo_path)
            if not success:
                return f"❌ Error finding branch point: {base_commit}"
        
        base_commit = CommitHash(base_commit.strip())
        
        # Count commits to squash
        success, commit_count = run_git_command(
            ["rev-list", "--count", f"{base_commit}..HEAD"], repo_path
        )
        
        squashed_count = 0
        if success and int(commit_count.strip()) > 1:
            squashed_count = int(commit_count.strip())
            # Reset and create single commit
            success, output = run_git_command(["reset", "--soft", base_commit], repo_path)
            if success:
                # Create squash commit bypassing hooks initially
                success, output = run_git_command(
                    ["commit", "-m", commit_message, "--no-verify"], repo_path
                )
                if not success:
                    return f"❌ Error creating squash commit: {output}"
                
                # Let hooks run and potentially fix formatting
                success, output = run_git_command(
                    ["commit", "--amend", "--no-edit"], repo_path
                )
                if not success:
                    return f"❌ Error running hooks on squash commit: {output}"
                
                # Give file watcher a moment to detect hook changes
                time.sleep(2)
            else:
                return f"❌ Error resetting to base commit: {output}"
        
        # Checkout main and pull
        success, output = run_git_command(["checkout", "main"], repo_path)
        if not success:
            return f"❌ Error checking out main: {output}"
            
        success, output = run_git_command(["pull", "origin", "main"], repo_path)
        if not success:
            return f"❌ Error pulling latest main: {output}"
        
        # Checkout vibe branch
        success, output = run_git_command(["checkout", branch_name], repo_path)
        if not success:
            return f"❌ Error checking out vibe branch: {output}"
        
        # Try to rebase
        rebase_success, rebase_output = run_git_command(["rebase", "main"], repo_path)
        had_conflicts = False
        
        if not rebase_success:
            had_conflicts = True
            # Try to abort the rebase if it failed
            run_git_command(["rebase", "--abort"], repo_path)
            warnings.append("Had to force push due to rebase conflicts. Review the PR carefully.")
            
            # Force push instead
            success, output = run_git_command(
                ["push", "-f", "-u", "origin", branch_name], repo_path
            )
            if not success:
                return f"❌ Error: Rebase failed and couldn't force push: {rebase_output}\nPush error: {output}"
        else:
            # Always force push after successful rebase since we've rewritten history
            success, output = run_git_command(
                ["push", "-f", "-u", "origin", branch_name], repo_path
            )
            if not success:
                return f"❌ Error force pushing rebased branch: {output}"
        
        # Parse commit message for PR
        pr_title, pr_body = parse_commit_message(commit_message)
        
        # Create PR using GitHub CLI
        pr_url = None
        success, output = run_command(
            ["gh", "pr", "create", "--title", pr_title, "--body", pr_body], repo_path
        )
        
        if success and output:
            pr_url = PRUrl(output.strip())
        
        # Return to main branch
        success, output = run_git_command(["checkout", "main"], repo_path)
        if not success:
            return f"❌ Error switching back to main: {output}"
        
        # NOW we can stop the file watcher - all git operations are complete
        session.state.observer.stop()
        session.state.observer.join(timeout=2)
        session.state.commit_event.set()  # Wake up commit worker to exit
        
        # Reset state
        with atomic_state_transition(session):
            session.transition_to(IdleState())
        
        result = VibeStopResult(
            success=True,
            pr_url=pr_url,
            message=f"🏁 Stopped vibing! Squashed commits into: '{commit_message}', rebased on main, and pushed to origin.",
            squashed_commits=squashed_count,
            had_conflicts=had_conflicts,
            warnings=warnings if warnings else None
        )
        
        return str(result)
        
    except Exception as e:
        # Reset state on error
        if isinstance(session.state, VibingState):
            session.state.observer.stop()
        with atomic_state_transition(session):
            session.transition_to(IdleState())
        return f"❌ Error stopping vibe session: {e}"


@mcp.tool()
@beartype
def stash_and_vibe() -> str:
    """📦 Stash uncommitted changes and start a new vibe session from main. Your changes will be saved and can be restored later with 'git stash pop'."""
    try:
        repo_path = find_git_repo()
        
        has_changes, _ = has_uncommitted_changes(repo_path)
        if not has_changes:
            return "No changes to stash. Proceeding to start vibe session..."
        
        success, output = run_git_command(
            ["stash", "push", "-m", "Pre-vibe stash"], repo_path
        )
        if not success:
            return f"❌ Error stashing changes: {output}"
        
        # Reset to idle state and start vibing
        with atomic_state_transition(session):
            session.transition_to(IdleState())
        
        result = start_vibing_from_state(IdleState(), repo_path)
        return str(result) + "\n\n💡 Your changes are stashed. Run 'git stash pop' after vibing to restore them."
        
    except Exception as e:
        return f"❌ Error: {e}"


@mcp.tool()
@beartype
def commit_and_vibe() -> str:
    """💾 Commit all uncommitted changes as 'WIP' and start a new vibe session from main."""
    try:
        repo_path = find_git_repo()
        
        has_changes, _ = has_uncommitted_changes(repo_path)
        if not has_changes:
            return "No changes to commit. Proceeding to start vibe session..."
        
        # Add and commit
        success, _ = run_git_command(["add", "."], repo_path)
        if not success:
            return "❌ Error adding changes. Check if files are ignored by .gitignore"
        
        success, output = run_git_command(
            ["commit", "-m", "WIP: Pre-vibe commit"], repo_path
        )
        if not success:
            return f"❌ Error committing changes: {output}"
        
        # Reset to idle state and start vibing
        with atomic_state_transition(session):
            session.transition_to(IdleState())
        
        result = start_vibing_from_state(IdleState(), repo_path)
        return str(result) + "\n\n✅ Your changes were committed as 'WIP: Pre-vibe commit'"
        
    except Exception as e:
        return f"❌ Error: {e}"


@mcp.tool()
@beartype
def vibe_from_here() -> str:
    """🌿 Start vibing from the current branch with all existing changes. Any uncommitted changes will be auto-committed as part of the vibe session."""
    
    if isinstance(session.state, VibingState):
        return "Already vibing! Session is active and auto-committing changes."
    
    try:
        repo_path = find_git_repo()
        current_branch = get_current_branch(repo_path)
        
        if not current_branch:
            return "❌ Error: Could not determine current branch"
        
        # Generate vibe branch if needed
        if not is_vibe_branch(current_branch):
            timestamp = generate_timestamp()
            branch_name = BranchName(f"vibe-{timestamp}")
            
            success, output = run_git_command(
                ["checkout", "-b", branch_name], repo_path
            )
            if not success:
                return f"❌ Error creating branch: {output}"
        else:
            branch_name = current_branch
        
        # Start file watching
        new_state = start_file_watcher(repo_path, branch_name)
        with atomic_state_transition(session):
            session.transition_to(new_state)
        
        # Check for uncommitted changes
        has_changes, _ = has_uncommitted_changes(repo_path)
        
        if has_changes:
            # Trigger immediate commit
            session.state.commit_event.set()
            return f"🚀 Started vibing on branch '{branch_name}'! Existing uncommitted changes will be auto-committed shortly."
        else:
            return f"🚀 Started vibing on branch '{branch_name}'! Auto-committing future changes."
        
    except Exception as e:
        return f"❌ Error starting vibe session: {e}"


@mcp.tool()
@beartype
def vibe_status() -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle. Use this to understand the current state.
    
    Test change to verify auto-commit with new .gitignore filtering."""
    try:
        repo_path = find_git_repo()
        current_branch = get_current_branch(repo_path)
        
        # Check active vibe session
        if isinstance(session.state, VibingState):
            if current_branch == session.state.branch_name:
                return f"🟢 VIBING: Active session on branch '{session.state.branch_name}' - auto-committing changes on file modifications"
            else:
                # State inconsistent, reset
                with atomic_state_transition(session):
                    session.transition_to(IdleState())
        
        # Check dirty state
        if isinstance(session.state, DirtyState):
            return f"🟡 DIRTY: Uncommitted changes on branch '{session.state.branch_name}'. Choose commit_and_vibe(), stash_and_vibe(), or vibe_from_here()."
        
        # Check if on vibe branch but idle
        if current_branch and is_vibe_branch(current_branch):
            return f"🟡 VIBE BRANCH DETECTED: On branch '{current_branch}' but session is idle. Call start_vibing() to resume or vibe_from_here() to restart watching."
        
        return "🔵 IDLE: Ready to start vibing. Call start_vibing() to begin!"
        
    except Exception as e:
        return f"⚪ NOT INITIALIZED: Error checking repository status: {e}"


@beartype
def signal_handler(sig: int, frame) -> None:
    """Handle SIGINT/SIGTERM gracefully"""
    if isinstance(session.state, VibingState):
        session.state.observer.stop()
    session.transition_to(IdleState())
    sys.exit(0)


def main():
    """Main entry point for the MCP server"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    mcp.run()


if __name__ == "__main__":
    main()