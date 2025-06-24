"""Tests demonstrating type safety improvements"""

import tempfile
from pathlib import Path

import pytest
from beartype.roar import BeartypeCallHintViolation

from vibe_git.type_utils import GitPath, validate_git_path, is_vibe_branch
from vibe_git.git_utils import find_git_repo, get_current_branch, run_command


def test_git_path_validation():
    """Test that GitPath validation works correctly"""
    
    # Create a temporary directory without .git
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Should fail - not a git repo
        with pytest.raises(ValueError, match="is not a git repository"):
            validate_git_path(tmp_path)
        
        # Create .git directory
        (tmp_path / ".git").mkdir()
        
        # Should succeed now
        git_path = validate_git_path(tmp_path)
        assert isinstance(git_path, Path)
        assert (git_path / ".git").exists()


def test_is_vibe_branch():
    """Test vibe branch detection"""
    assert is_vibe_branch("vibe-1234567")
    assert is_vibe_branch("vibe-feature-x")
    assert not is_vibe_branch("main")
    assert not is_vibe_branch("feature/vibe-like")


def test_command_dispatch():
    """Test that command dispatch works with both string and list"""
    # String version
    success, output = run_command("echo hello")
    assert success
    assert output == "hello"
    
    # List version  
    success, output = run_command(["echo", "hello", "world"])
    assert success
    assert output == "hello world"


def test_beartype_validation():
    """Test that beartype catches type errors at runtime"""
    from plum.resolver import NotFoundLookupError
    
    # With plum, incorrect types result in NotFoundLookupError
    with pytest.raises(NotFoundLookupError):
        # Passing int instead of list[str] or str
        run_command(123)  # type: ignore
    
    # beartype will catch wrong parameter types
    with pytest.raises(BeartypeCallHintViolation):
        # Passing dict instead of Path
        run_command("echo test", cwd={"not": "a path"})  # type: ignore


@pytest.mark.skipif(
    not Path.cwd().joinpath(".git").exists(),
    reason="Not in a git repository"
)
def test_git_utilities():
    """Test git utilities with type safety"""
    
    # Find repo should return a GitPath
    repo = find_git_repo()
    assert (repo / ".git").exists()
    
    # Get current branch should return BranchName or None
    branch = get_current_branch(repo)
    if branch:
        assert isinstance(branch, str)
        # If on a vibe branch, it should be detected
        if branch.startswith("vibe-"):
            assert is_vibe_branch(branch)