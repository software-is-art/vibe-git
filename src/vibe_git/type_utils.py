"""Type utilities for vibe-git with beartype validation"""

from pathlib import Path
from typing import NewType, TypeAlias

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

# Command execution types
CommandResult: TypeAlias = tuple[bool, str]  # noqa: UP040
"""Result of command execution: (success, output)"""


# Validation helpers
def is_vibe_branch(branch: str) -> bool:
    """Check if a branch name is a vibe branch"""
    return branch.startswith("vibe-")


def validate_git_path(path: Path) -> GitPath:
    """Validate and convert a Path to GitPath"""
    if not (path / ".git").exists():
        raise ValueError(f"{path} is not a git repository")
    return GitPath(path)
