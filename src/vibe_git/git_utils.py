"""Git utilities with beartype validation and plum dispatch"""

import subprocess
from pathlib import Path

from plum import dispatch

from .type_utils import BranchName, CommandResult, GitPath


def find_git_repo() -> GitPath:
    """Find the git repository root with type safety"""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".git").exists():
            return GitPath(current)
        current = current.parent
    raise RuntimeError("Not in a git repository")


@dispatch
def run_command(args: list[str], cwd: Path | None = None) -> CommandResult:
    """Run command with list of arguments"""
    try:
        # Only use find_git_repo() if we're running a git command
        if cwd is None and len(args) > 0 and args[0] == "git":
            try:
                cwd = find_git_repo()
            except RuntimeError:
                # Not in a git repo, use current directory
                cwd = Path.cwd()

        result = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0, result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return False, str(e)


@dispatch
def run_command(command: str, cwd: Path | None = None) -> CommandResult:  # noqa: F811
    """Run command with single string (auto-splits)"""
    return run_command(command.split(), cwd)


def run_git_command(args: list[str], cwd: Path | None = None) -> CommandResult:
    """Run a git command with type safety"""
    return run_command(["git"] + args, cwd)


@dispatch
def get_current_branch(repo_path: GitPath) -> BranchName | None:
    """Get current branch name with type safety - with repo_path"""
    success, output = run_git_command(["branch", "--show-current"], repo_path)
    if success and output:
        return BranchName(output.strip())
    return None


@dispatch
def get_current_branch() -> BranchName | None:  # noqa: F811
    """Get current branch name with type safety - find repo automatically"""
    return get_current_branch(find_git_repo())


@dispatch
def has_uncommitted_changes(repo_path: GitPath) -> tuple[bool, str]:
    """Check for uncommitted changes with details - with repo_path"""
    success, output = run_git_command(["status", "--porcelain"], repo_path)
    has_changes = success and output.strip() != ""
    return has_changes, output.strip() if has_changes else ""


@dispatch
def has_uncommitted_changes() -> tuple[bool, str]:  # noqa: F811
    """Check for uncommitted changes with details - find repo automatically"""
    return has_uncommitted_changes(find_git_repo())


@dispatch
def checkout_branch(branch: str, repo_path: GitPath) -> CommandResult:
    """Checkout a branch (string version with repo)"""
    return run_git_command(["checkout", branch], repo_path)


@dispatch
def checkout_branch(branch: BranchName, repo_path: GitPath) -> CommandResult:  # noqa: F811
    """Checkout a branch (BranchName version with repo)"""
    return run_git_command(["checkout", str(branch)], repo_path)


@dispatch
def checkout_branch(branch: str) -> CommandResult:  # noqa: F811
    """Checkout a branch (string version, auto-find repo)"""
    return checkout_branch(branch, find_git_repo())


@dispatch
def checkout_branch(branch: BranchName) -> CommandResult:  # noqa: F811
    """Checkout a branch (BranchName version, auto-find repo)"""
    return checkout_branch(branch, find_git_repo())


@dispatch
def create_branch(branch: str, repo_path: GitPath) -> CommandResult:
    """Create and checkout a new branch (string version with repo)"""
    return run_git_command(["checkout", "-b", branch], repo_path)


@dispatch
def create_branch(branch: BranchName, repo_path: GitPath) -> CommandResult:  # noqa: F811
    """Create and checkout a new branch (BranchName version with repo)"""
    return run_git_command(["checkout", "-b", str(branch)], repo_path)


@dispatch
def create_branch(branch: str) -> CommandResult:  # noqa: F811
    """Create and checkout a new branch (string version, auto-find repo)"""
    return create_branch(branch, find_git_repo())


@dispatch
def create_branch(branch: BranchName) -> CommandResult:  # noqa: F811
    """Create and checkout a new branch (BranchName version, auto-find repo)"""
    return create_branch(branch, find_git_repo())


@dispatch
def ensure_on_main_branch(repo_path: GitPath) -> str | None:
    """Ensure we're on main/master branch, returns branch name if successful - with repo"""
    # Try main first
    success, _ = checkout_branch("main", repo_path)
    if success:
        return "main"

    # Fall back to master
    success, _ = checkout_branch("master", repo_path)
    if success:
        return "master"

    return None


@dispatch
def ensure_on_main_branch() -> str | None:  # noqa: F811
    """Ensure we're on main/master branch, returns branch name if successful - auto-find repo"""
    return ensure_on_main_branch(find_git_repo())
