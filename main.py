#!/usr/bin/env python3
"""
vibe-git MCP Server - Friction-free git workflows for vibe coding

Enables developers to focus on code while git operations happen automatically.
"""

import asyncio
import os
import subprocess
import time
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from threading import Thread, Event
import signal
import sys

from fastmcp import FastMCP
from pydantic import BaseModel
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


@dataclass 
class VibeSession:
    """Represents the current vibe session state"""
    branch_name: Optional[str] = None
    is_vibing: bool = False
    observer: Optional[Observer] = None
    commit_event: Optional[Event] = None


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


def run_git_command(args: list[str], cwd: Optional[Path] = None) -> tuple[bool, str]:
    """Run a git command and return (success, output)"""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd or find_git_repo(),
            capture_output=True,
            text=True,
            check=False
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
            '.git', '__pycache__', '.pytest_cache', '.venv', 'node_modules',
            '.DS_Store', '*.pyc', '*.pyo', '*.swp', '*.tmp', '.coverage'
        ]
        
        for pattern in ignore_patterns:
            if pattern.startswith('*'):
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


@mcp.tool()
def start_vibing() -> str:
    """🚀 CALL THIS FIRST before making any code changes! Creates a new git branch and starts auto-committing all file changes every second. Safe to call multiple times - will not create duplicate sessions."""
    global session
    
    if session.is_vibing:
        return "Already vibing! Session is active and auto-committing changes."
    
    try:
        repo_path = find_git_repo()
        
        # Generate branch name
        timestamp = int(time.time())
        branch_name = f"vibe-{timestamp}"
        
        # Check current branch
        success, current_branch = run_git_command(["branch", "--show-current"], repo_path)
        if success and current_branch.startswith("vibe-"):
            # We're already on a vibe branch - reuse it instead of creating a new one
            session.branch_name = current_branch
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
            
            return f"🚀 Started vibing! Reusing existing vibe branch '{current_branch}' and auto-committing changes on file modifications."
        
        # Ensure we're on main branch
        success, _ = run_git_command(["checkout", "main"], repo_path)
        if not success:
            # Try master if main doesn't exist
            success, _ = run_git_command(["checkout", "master"], repo_path)
            if not success:
                return "❌ Error: Could not checkout main/master branch. Try manually switching to main first."
        
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
        
        return f"🚀 Started vibing! Created branch '{branch_name}' and auto-committing changes on file modifications."
        
    except Exception as e:
        return f"❌ Error starting vibe session: {e}"


@mcp.tool()
def stop_vibing(commit_message: str) -> str:
    """🏁 Call this ONLY when the user explicitly says to stop or asks you to stop the session. Squashes all auto-commits into a single commit with your message, rebases onto latest main, and creates a PR. Do NOT call this automatically - wait for user confirmation before stopping. Safe to call even if not vibing."""
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
            success, output = run_git_command(["merge-base", "master", "HEAD"], repo_path)
            if not success:
                return f"❌ Error finding branch point: {output}"
        
        base_commit = output.strip()
        
        # Count commits to squash
        success, output = run_git_command(["rev-list", "--count", f"{base_commit}..HEAD"], repo_path)
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
        success, output = run_git_command(["push", "-u", "origin", branch_name], repo_path)
        if not success:
            return f"❌ Error pushing branch: {output}"
        
        # Try to create PR using GitHub CLI
        success, output = run_git_command(
            ["gh", "pr", "create", "--title", commit_message, "--body", f"Vibe session completed.\n\n{commit_message}"],
            repo_path
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
def vibe_status() -> str:
    """📊 Check the current vibe session status - whether you're currently vibing or idle. Use this to understand the current state."""
    try:
        repo_path = find_git_repo()
        
        if session.is_vibing and session.branch_name:
            # Get current branch to confirm
            success, current_branch = run_git_command(["branch", "--show-current"], repo_path)
            if success and current_branch == session.branch_name:
                return f"🟢 VIBING: Active session on branch '{session.branch_name}' - auto-committing changes on file modifications"
            else:
                # Session state is inconsistent, reset it
                session.is_vibing = False
                session.branch_name = None
                return "🔵 IDLE: Ready to start vibing (session state was reset due to branch mismatch)"
        else:
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