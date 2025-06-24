"""Git utilities with beartype validation and plum dispatch"""

import subprocess
from pathlib import Path

from beartype import beartype
from plum import dispatch

from .type_utils import CommandResult, GitPath, BranchName


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
    """Run command with list of arguments"""
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
    """Run command with single string (auto-splits)"""
    return run_command(command.split(), cwd)


@beartype
def run_git_command(args: list[str], cwd: Path | None = None) -> CommandResult:
    """Run a git command with type safety"""
    return run_command(["git"] + args, cwd)


@beartype
def get_current_branch(repo_path: GitPath | None = None) -> BranchName | None:
    """Get current branch name with type safety"""
    repo = repo_path or find_git_repo()
    success, output = run_git_command(["branch", "--show-current"], repo)
    if success and output:
        return BranchName(output.strip())
    return None


@beartype
def has_uncommitted_changes(repo_path: GitPath | None = None) -> tuple[bool, str]:
    """Check for uncommitted changes with details"""  
    repo = repo_path or find_git_repo()
    success, output = run_git_command(["status", "--porcelain"], repo)
    has_changes = success and output.strip() != ""
    return has_changes, output.strip() if has_changes else ""


@beartype
def checkout_branch(branch: str | BranchName, repo_path: GitPath | None = None) -> CommandResult:
    """Checkout a branch with type safety"""
    repo = repo_path or find_git_repo()
    return run_git_command(["checkout", str(branch)], repo)


@beartype
def create_branch(branch: str | BranchName, repo_path: GitPath | None = None) -> CommandResult:
    """Create and checkout a new branch"""
    repo = repo_path or find_git_repo()
    return run_git_command(["checkout", "-b", str(branch)], repo)


@beartype
def ensure_on_main_branch(repo_path: GitPath | None = None) -> str | None:
    """Ensure we're on main/master branch, returns branch name if successful"""
    repo = repo_path or find_git_repo()
    
    # Try main first
    success, _ = checkout_branch("main", repo)
    if success:
        return "main"
    
    # Fall back to master
    success, _ = checkout_branch("master", repo) 
    if success:
        return "master"
        
    return None