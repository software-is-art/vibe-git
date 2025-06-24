"""Result types for better type safety instead of tuples"""

from dataclasses import dataclass

from .type_utils import BranchName, PRBody, PRTitle


@dataclass(frozen=True)
class CommandResult:
    """Result of command execution with structured data"""
    
    success: bool
    output: str
    
    def __iter__(self):
        """Allow tuple unpacking for backwards compatibility"""
        return iter((self.success, self.output))
    
    def __getitem__(self, index: int):
        """Allow indexing for backwards compatibility"""
        if index == 0:
            return self.success
        elif index == 1:
            return self.output
        else:
            raise IndexError("CommandResult index out of range")


@dataclass(frozen=True)
class ChangesResult:
    """Result of checking for uncommitted changes"""
    
    has_changes: bool
    details: str
    
    def __iter__(self):
        """Allow tuple unpacking for backwards compatibility"""
        return iter((self.has_changes, self.details))
    
    def __getitem__(self, index: int):
        """Allow indexing for backwards compatibility"""
        if index == 0:
            return self.has_changes
        elif index == 1:
            return self.details
        else:
            raise IndexError("ChangesResult index out of range")


@dataclass(frozen=True)
class ParsedMessage:
    """Result of parsing a commit message"""
    
    title: PRTitle
    body: PRBody
    
    def __iter__(self):
        """Allow tuple unpacking for backwards compatibility"""
        return iter((self.title, self.body))
    
    def __getitem__(self, index: int):
        """Allow indexing for backwards compatibility"""
        if index == 0:
            return self.title
        elif index == 1:
            return self.body
        else:
            raise IndexError("ParsedMessage index out of range")


@dataclass(frozen=True)
class BranchCheckResult:
    """Result of checking current branch"""
    
    branch_name: BranchName | None
    is_vibe_branch: bool
    
    @property
    def has_branch(self) -> bool:
        """Check if we have a valid branch"""
        return self.branch_name is not None