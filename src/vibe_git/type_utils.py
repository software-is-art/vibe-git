"""Type utilities for vibe-git with beartype validation"""

import re
from pathlib import Path
from typing import Literal, NewType, TypeAlias

from beartype.typing import Annotated
from beartype.vale import Is

# Validated path types
GitPath = Annotated[Path, Is[lambda p: (p / ".git").exists()]]
"""A Path that is guaranteed to be inside a git repository"""

# Semantic string types
BranchName = NewType("BranchName", str)
"""A validated git branch name"""

CommitHash = NewType("CommitHash", str)
"""A git commit hash"""

CommitMessage = NewType("CommitMessage", str)
"""A git commit message"""

PRTitle = NewType("PRTitle", str)
"""A pull request title"""

PRBody = NewType("PRBody", str)
"""A pull request body/description"""

# Command execution types
CommandResult: TypeAlias = tuple[bool, str]  # noqa: UP040
"""Result of command execution: (success, output)"""

# Additional semantic types
MainBranchName = Literal["main", "master"]
"""Valid main branch names"""

FilePattern = NewType("FilePattern", str)
"""A file glob pattern"""

GitRemote = NewType("GitRemote", str)  
"""A git remote name like 'origin'"""

RelativePath = Annotated[Path, Is[lambda p: not p.is_absolute()]]
"""A path that must be relative"""

ValidBranchName = Annotated[str, Is[lambda s: bool(re.match(r'^[a-zA-Z0-9_\-./]+$', s))]]
"""A valid git branch name"""

NonEmptyString = Annotated[str, Is[lambda s: len(s.strip()) > 0]]
"""A string that cannot be empty or only whitespace"""

ValidTimestamp = Annotated[int, Is[lambda t: t > 0]]
"""A positive timestamp value"""

ValidCommitMessage = Annotated[str, Is[lambda s: len(s.strip()) > 0 and '\n' not in s.strip()[:50]]]
"""A valid commit message with non-empty first line under 50 chars"""

VibeBranchName = Annotated[str, Is[lambda s: s.startswith("vibe-")]]
"""A branch name that starts with 'vibe-'"""


# Validation helpers
def is_vibe_branch(branch: str) -> bool:
    """Check if a branch name is a vibe branch"""
    return branch.startswith("vibe-")


def as_vibe_branch(branch: str) -> VibeBranchName:
    """Convert and validate a branch name as a vibe branch"""
    if not is_vibe_branch(branch):
        raise ValueError(f"{branch} is not a vibe branch (must start with 'vibe-')")
    return VibeBranchName(branch)


def validate_git_path(path: Path) -> GitPath:
    """Validate and convert a Path to GitPath"""
    if not (path / ".git").exists():
        raise ValueError(f"{path} is not a git repository")
    return GitPath(path)
