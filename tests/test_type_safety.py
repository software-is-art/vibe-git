"""Tests demonstrating type safety improvements"""

import tempfile
from pathlib import Path

import pytest
from beartype.roar import BeartypeCallHintViolation

from vibe_git.git_utils import find_git_repo, get_current_branch
from vibe_git.type_utils import is_vibe_branch, validate_git_path


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


def test_git_path_exact_check():
    """Test that we're checking for exactly .git"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create .gitx directory (not .git)
        (tmp_path / ".gitx").mkdir()

        # Should fail because it's looking for .git not .gitx
        with pytest.raises(ValueError, match="is not a git repository"):
            validate_git_path(tmp_path)


def test_git_path_requires_exact_name():
    """Test that validate_git_path checks for the exact '.git' string"""
    # This test ensures the mutation from ".git" to ".GIT" is caught
    # We mock the exists() method to control the behavior

    from unittest.mock import patch

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create a mock that tracks what path was checked
        checked_paths = []

        def mock_exists(self):
            # Record the path being checked
            checked_paths.append(str(self))
            # Only return True if checking for lowercase .git
            if str(self).endswith("/.git"):
                return True
            return False

        # Patch Path.exists to use our mock
        with patch.object(Path, "exists", mock_exists):
            # This should succeed because we return True for .git
            result = validate_git_path(tmp_path)
            assert result == tmp_path

            # Verify that it checked for lowercase .git
            assert any(path.endswith("/.git") for path in checked_paths), (
                "validate_git_path should check for lowercase '.git'"
            )


def test_is_vibe_branch():
    """Test vibe branch detection"""
    assert is_vibe_branch("vibe-1234567")
    assert is_vibe_branch("vibe-feature-x")
    assert not is_vibe_branch("main")
    assert not is_vibe_branch("feature/vibe-like")


def test_command_dispatch():
    """Test that command dispatch works with both string and list"""
    # Import run_command from git_utils explicitly
    from vibe_git.git_utils import run_command
    import sys
    from pathlib import Path
    
    # Use a specific directory to avoid issues with test pollution
    # Use the temp directory or current directory
    test_dir = Path.cwd()
    
    # Test list version - this is the primary interface
    success, output = run_command([sys.executable, "-c", "print('hello')"], cwd=test_dir)
    assert success, f"List command failed: {output}"
    assert output.strip() == "hello", f"Expected 'hello', got '{output}'"

    # Test string version - it should split and call the list version
    # Use a simple Python command to avoid shell quoting issues
    success, output = run_command(f"{sys.executable} --version", cwd=test_dir)
    assert success, f"String command failed: {output}"
    assert "Python" in output, f"Expected 'Python' in output, got '{output}'"


def test_beartype_validation():
    """Test that beartype catches type errors at runtime"""
    from plum.resolver import NotFoundLookupError
    from vibe_git.git_utils import run_command

    # With plum, incorrect types result in NotFoundLookupError
    with pytest.raises(NotFoundLookupError):
        # Passing int instead of list[str] or str
        run_command(123)  # type: ignore

    # beartype will catch wrong parameter types
    with pytest.raises(BeartypeCallHintViolation):
        # Passing dict instead of Path
        run_command("echo test", cwd={"not": "a path"})  # type: ignore


@pytest.mark.skipif(
    not Path.cwd().joinpath(".git").exists(), reason="Not in a git repository"
)
def test_git_utilities():
    """Test git utilities with type safety"""

    # Find repo should return a GitPath
    try:
        repo = find_git_repo()
    except RuntimeError:
        # If we're not in a git repo (e.g., running from tests dir), skip
        pytest.skip("Not in a git repository")
    assert (repo / ".git").exists()

    # Get current branch should return BranchName or None
    branch = get_current_branch(repo)
    if branch:
        assert isinstance(branch, str)
        # If on a vibe branch, it should be detected
        if branch.startswith("vibe-"):
            assert is_vibe_branch(branch)
