#!/usr/bin/env python3
"""
Focused tests for vibe status logic only.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from vibe_git.vibe_status_only import (
    VibeSession,
    find_git_repo,
    run_git_command,
    vibe_status,
)


class GitRepoFixture:
    """Helper class to create and manage temporary git repositories for testing."""

    def __init__(self):
        self.temp_dir = None
        self.repo_path = None
        self.original_cwd = None

    def __enter__(self):
        """Create a temporary git repository."""
        self.temp_dir = tempfile.mkdtemp(prefix="vibe_git_test_")
        self.repo_path = Path(self.temp_dir)

        # Store original directory before changing
        try:
            self.original_cwd = os.getcwd()
        except FileNotFoundError:
            # If current directory was deleted, use home as fallback
            self.original_cwd = os.path.expanduser("~")

        # Change to temp directory
        os.chdir(self.repo_path)

        # Initialize git repo
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)

        # Create initial commit
        (self.repo_path / "README.md").write_text("# Test Repo")
        subprocess.run(["git", "add", "README.md"], check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)

        # Ensure we're on main branch
        result = subprocess.run(
            ["git", "branch", "--show-current"], capture_output=True, text=True
        )
        current_branch = result.stdout.strip() if result.returncode == 0 else "master"

        if current_branch != "main":
            subprocess.run(["git", "branch", "-M", "main"], check=True)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up temporary repository."""
        # Change back to original directory safely
        if self.original_cwd and os.path.exists(self.original_cwd):
            os.chdir(self.original_cwd)
        else:
            os.chdir(os.path.expanduser("~"))

        # Remove temp directory
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)


def test_status_idle_on_main():
    """Test status shows idle when on main branch."""
    with GitRepoFixture():
        session = VibeSession()
        result = vibe_status(session)
        assert "🔵 IDLE" in result
        assert "Ready to start vibing" in result


def test_status_detects_vibe_branch():
    """Test status detects when on vibe branch but not vibing."""
    with GitRepoFixture():
        # Create and checkout a vibe branch manually
        subprocess.run(["git", "checkout", "-b", "vibe-12345"], check=True)

        session = VibeSession()
        result = vibe_status(session)
        assert "🟡 VIBE BRANCH DETECTED" in result
        assert "vibe-12345" in result


def test_status_shows_active_session():
    """Test status shows active when vibing."""
    with GitRepoFixture():
        # Manually set session state as vibing
        session = VibeSession()
        session.is_vibing = True
        session.branch_name = "vibe-test"

        # Create the branch
        subprocess.run(["git", "checkout", "-b", "vibe-test"], check=True)

        # Check status
        result = vibe_status(session)
        assert "🟢 VIBING" in result
        assert "auto-committing changes" in result


def test_status_handles_inconsistent_state():
    """Test status resets when session branch doesn't match current branch."""
    with GitRepoFixture():
        # Set up inconsistent state
        session = VibeSession()
        session.is_vibing = True
        session.branch_name = "vibe-wrong"

        # We're on main, but session thinks we're on vibe-wrong
        vibe_status(session)

        # Should reset session and return idle
        assert session.is_vibing is False
        assert session.branch_name is None


def test_status_handles_git_errors():
    """Test status handles git command failures gracefully."""
    # Test outside git repo
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        session = VibeSession()
        result = vibe_status(session)
        assert "⚪ NOT INITIALIZED" in result or "Error" in result


def test_run_git_command_with_explicit_cwd():
    """Test run_git_command with explicit cwd parameter."""
    with GitRepoFixture() as fixture:
        # Test with explicit cwd
        success, output = run_git_command(["status"], fixture.repo_path)
        assert success is True

        # Test with None cwd (should use find_git_repo)
        success2, output2 = run_git_command(["status"], None)
        assert success2 is True


def test_run_git_command_error_conditions():
    """Test run_git_command error handling."""
    with GitRepoFixture() as fixture:
        # Test invalid git command
        success, output = run_git_command(["invalid-command"], fixture.repo_path)
        assert success is False
        assert len(output) > 0


def test_find_git_repo_boundary_conditions():
    """Test find_git_repo edge cases."""
    with GitRepoFixture():
        # Should find repo successfully
        repo_path = find_git_repo()
        assert repo_path.exists()
        assert (repo_path / ".git").exists()


def test_vibe_status_uses_found_repo_path():
    """Test that vibe_status passes the correct repo path to run_git_command."""
    with GitRepoFixture():
        session = VibeSession()

        # Mock find_git_repo to return a specific path
        import unittest.mock

        with (
            unittest.mock.patch("vibe_git.vibe_status_only.find_git_repo") as mock_find,
            unittest.mock.patch(
                "vibe_git.vibe_status_only.run_git_command"
            ) as mock_run,
        ):
            mock_find.return_value = Path("/fake/repo")
            mock_run.return_value = (True, "main")

            vibe_status(session)

            # Verify find_git_repo was called
            mock_find.assert_called_once()
            # Verify run_git_command was called with the repo path
            mock_run.assert_called_with(
                ["branch", "--show-current"], Path("/fake/repo")
            )


def test_find_git_repo_not_in_repo():
    """Test find_git_repo when not in a git repository."""
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        try:
            find_git_repo()
            raise AssertionError("Should have raised RuntimeError")
        except RuntimeError as e:
            assert "Not in a git repository" in str(e)


def test_vibesession_initialization():
    """Test VibeSession initializes with correct default values."""
    session = VibeSession()
    assert session.branch_name is None
    assert session.is_vibing is False
    assert session.observer is None
    assert session.commit_event is None


def test_vibe_status_git_command_failure():
    """Test vibe_status handles git command failures."""
    with GitRepoFixture():
        session = VibeSession()

        # Mock run_git_command to return failure
        import unittest.mock

        with unittest.mock.patch(
            "vibe_git.vibe_status_only.run_git_command"
        ) as mock_run:
            mock_run.return_value = (False, "error output")

            result = vibe_status(session)
            # Check exact string to catch string literal mutations
            assert result == "⚪ NOT INITIALIZED: Could not determine current branch"


def test_run_git_command_exception_handling():
    """Test run_git_command exception handling."""
    import unittest.mock

    with unittest.mock.patch("subprocess.run") as mock_run:
        # Make subprocess.run raise an exception
        mock_run.side_effect = Exception("Command failed")

        success, output = run_git_command(["status"], Path("/fake/path"))
        assert success is False
        assert "Command failed" in output


def test_find_git_repo_exact_path_check():
    """Test find_git_repo checks for exact .git path."""
    import unittest.mock

    # Mock the entire find_git_repo function to test the mutation
    with unittest.mock.patch("vibe_git.vibe_status_only.Path") as MockPath:
        mock_cwd = unittest.mock.MagicMock()
        mock_parent = unittest.mock.MagicMock()

        # Set up the path hierarchy
        MockPath.cwd.return_value = mock_cwd
        mock_cwd.parent = mock_parent
        mock_parent.parent = mock_parent  # Make parent of parent be itself (root)

        # Mock the / operator to return a new mock
        def mock_div(self, other):
            result = unittest.mock.MagicMock()
            # .git exists, .GIT doesn't
            if other == ".git":
                result.exists.return_value = True
            elif other == ".GIT":
                result.exists.return_value = False
            else:
                result.exists.return_value = False
            return result

        mock_cwd.__truediv__ = mock_div
        mock_cwd.__ne__.return_value = True  # current != current.parent

        # Test that find_git_repo finds .git
        result = find_git_repo()
        assert result == mock_cwd

        # Now test with only .GIT existing (should fail)
        def mock_div_git_upper(self, other):
            result = unittest.mock.MagicMock()
            # Only .GIT exists, not .git
            if other == ".git":
                result.exists.return_value = False
            elif other == ".GIT":
                result.exists.return_value = True
            else:
                result.exists.return_value = False
            return result

        mock_cwd.__truediv__ = mock_div_git_upper
        mock_cwd.__ne__.side_effect = [
            True,
            False,
        ]  # First iteration: True, then False to exit loop

        # Reset the mock
        MockPath.cwd.return_value = mock_cwd

        try:
            find_git_repo()
            raise AssertionError("Should have raised RuntimeError")
        except RuntimeError as e:
            assert str(e) == "Not in a git repository"


def test_find_git_repo_exact_error_message():
    """Test find_git_repo error message is exact."""
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        try:
            find_git_repo()
            raise AssertionError("Should have raised RuntimeError")
        except RuntimeError as e:
            # Test exact error message to catch string mutations
            assert str(e) == "Not in a git repository"


def test_run_git_command_cwd_parameter_usage():
    """Test run_git_command actually uses cwd parameter vs falling back to find_git_repo."""
    with GitRepoFixture() as fixture:
        import unittest.mock

        # Mock find_git_repo to return a different path
        with unittest.mock.patch(
            "vibe_git.vibe_status_only.find_git_repo"
        ) as mock_find:
            mock_find.return_value = Path("/fake/fallback/path")

            # Call with explicit cwd - should NOT call find_git_repo
            success, output = run_git_command(["status"], fixture.repo_path)
            assert success is True
            # find_git_repo should not be called when cwd is provided
            mock_find.assert_not_called()


def test_run_git_command_subprocess_parameters():
    """Test run_git_command passes correct parameters to subprocess.run."""
    with GitRepoFixture() as fixture:
        import unittest.mock

        with unittest.mock.patch("subprocess.run") as mock_run:
            # Mock successful result
            mock_result = unittest.mock.MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "output"
            mock_result.stderr = ""
            mock_run.return_value = mock_result

            run_git_command(["status"], fixture.repo_path)

            # Verify subprocess.run was called with correct parameters
            mock_run.assert_called_once_with(
                ["git", "status"],
                cwd=fixture.repo_path,
                capture_output=True,
                text=True,
                check=False,
            )


def test_vibe_status_logic_conditions():
    """Test vibe_status logic conditions (and vs or)."""
    with GitRepoFixture():
        session = VibeSession()

        # Test case 1: is_vibing=True, branch_name=None (should NOT enter if block)
        session.is_vibing = True
        session.branch_name = None
        result = vibe_status(session)
        assert "🔵 IDLE" in result  # Should not enter the vibing block
        # Verify session was not reset
        assert session.is_vibing is True
        assert session.branch_name is None

        # Test case 2: is_vibing=False, branch_name="vibe-test" (should NOT enter if block)
        session.is_vibing = False
        session.branch_name = "vibe-test"
        result = vibe_status(session)
        assert "🔵 IDLE" in result  # Should not enter the vibing block
        # Verify session was not reset
        assert session.is_vibing is False
        assert session.branch_name == "vibe-test"

        # Test case 3: is_vibing=True, branch_name="vibe-test" (should enter if block)
        session.is_vibing = True
        session.branch_name = "vibe-test"
        # Create the branch so the condition works
        subprocess.run(["git", "checkout", "-b", "vibe-test"], check=True)
        result = vibe_status(session)
        assert "🟢 VIBING" in result


def test_vibe_status_exact_idle_message():
    """Test vibe_status returns exact idle message."""
    with GitRepoFixture():
        session = VibeSession()
        result = vibe_status(session)
        # Test exact string to catch string literal mutations
        assert result == "🔵 IDLE: Ready to start vibing. Call start_vibing() to begin!"


def test_vibe_status_output_processing():
    """Test vibe_status handles stdout vs stderr from git commands."""
    with GitRepoFixture():
        session = VibeSession()
        import unittest.mock

        # Test stdout.strip() path
        with unittest.mock.patch(
            "vibe_git.vibe_status_only.run_git_command"
        ) as mock_run:
            mock_run.return_value = (True, "  main  ")  # stdout with whitespace
            result = vibe_status(session)
            assert "🔵 IDLE" in result

        # Test the "or" logic in stdout.strip() or stderr.strip()
        with unittest.mock.patch(
            "vibe_git.vibe_status_only.run_git_command"
        ) as mock_run:
            mock_run.return_value = (True, "")  # empty stdout, should use stderr
            result = vibe_status(session)
            assert "🔵 IDLE" in result


def test_vibe_status_and_logic_with_branch_mismatch():
    """Test that session is reset when branch doesn't match (tests AND logic)."""
    with GitRepoFixture():
        session = VibeSession()

        # Set up a session with mismatched branch
        session.is_vibing = True
        session.branch_name = "vibe-wrong-branch"

        # We're on main, not vibe-wrong-branch
        result = vibe_status(session)

        # The session should be reset because current_branch != session.branch_name
        assert session.is_vibing is False
        assert session.branch_name is None
        assert "🔵 IDLE" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
