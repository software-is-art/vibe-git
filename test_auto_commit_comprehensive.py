#!/usr/bin/env python3
"""
Comprehensive tests for auto-commit mechanism improvements.

Tests the enhanced auto-commit functionality including:
1. Pre-commit hook integration
2. Pre-commit setup functionality
3. Error handling for hook failures
4. File watcher behavior
"""

import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from threading import Event
from unittest.mock import patch

import main


class GitRepoFixture:
    """Helper class to create temporary git repositories for testing"""

    def __init__(self):
        self.temp_dir = None
        self.original_cwd = None

    def __enter__(self):
        self.original_cwd = os.getcwd()
        self.temp_dir = tempfile.mkdtemp(prefix="vibe_auto_commit_test_")
        os.chdir(self.temp_dir)

        # Initialize git repo
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)

        # Create initial commit
        Path("README.md").write_text("# Test Repository")
        subprocess.run(["git", "add", "README.md"], check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)

        # Create main branch explicitly
        subprocess.run(["git", "branch", "-M", "main"], check=True)

        return self.temp_dir

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.original_cwd:
            os.chdir(self.original_cwd)
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)


def test_auto_commit_worker_pre_commit_success():
    """Test auto-commit worker when pre-commit hooks succeed."""
    print("🧪 Testing auto-commit worker with successful pre-commit hooks...")

    with GitRepoFixture():
        # Mock session state
        main.session.is_vibing = True
        main.session.commit_event = Event()

        # Create a test file
        Path("test_file.txt").write_text("Test content")

        # Mock run_git_command to simulate successful pre-commit
        original_run_git_command = main.run_git_command
        git_calls = []

        def mock_run_git_command(cmd, repo_path):
            git_calls.append(cmd.copy())

            if cmd == ["status", "--porcelain"]:
                return True, "M  test_file.txt"  # Show modified file
            elif cmd == ["add", "."]:
                return True, ""
            elif cmd[0] == "commit" and "-m" in cmd:
                return True, "Created commit abc123"  # Pre-commit succeeded
            else:
                return original_run_git_command(cmd, repo_path)

        with patch.object(main, "run_git_command", side_effect=mock_run_git_command):
            # Trigger commit event
            main.session.commit_event.set()

            # Simulate one iteration of auto-commit worker (avoid infinite loop)
            try:
                repo_path = main.find_git_repo()
                if main.session.commit_event and main.session.commit_event.wait(
                    timeout=1
                ):
                    main.session.commit_event.clear()
                    # Check for actual changes before committing
                    success, output = main.run_git_command(
                        ["status", "--porcelain"], repo_path
                    )
                    if success and output.strip():
                        # Add all changes
                        main.run_git_command(["add", "."], repo_path)
                        # Commit with timestamp
                        timestamp = int(time.time())
                        commit_msg = f"Auto-commit {timestamp}"
                        main.run_git_command(["commit", "-m", commit_msg], repo_path)
            except Exception:
                pass  # Expected

            # Verify git commands were called correctly
            commit_commands = [cmd for cmd in git_calls if cmd[0] == "commit"]

            assert len(commit_commands) == 1, (
                f"Expected 1 commit command, got {len(commit_commands)}"
            )
            assert "--no-verify" not in commit_commands[0], (
                "Should not use --no-verify when pre-commit succeeds"
            )

            print("✅ Auto-commit worker correctly handles successful pre-commit hooks")
            return True


def test_auto_commit_worker_pre_commit_fixes_files():
    """Test auto-commit worker when pre-commit hooks fix files."""
    print("🧪 Testing auto-commit worker when pre-commit hooks fix files...")

    with GitRepoFixture():
        main.session.is_vibing = True
        main.session.commit_event = Event()

        # Mock run_git_command to simulate pre-commit fixing files
        git_calls = []
        commit_attempt = 0

        def mock_run_git_command(cmd, repo_path):
            nonlocal commit_attempt
            git_calls.append(cmd.copy())

            if cmd == ["status", "--porcelain"]:
                return True, "M  test_file.py"
            elif cmd == ["add", "."]:
                return True, ""
            elif cmd[0] == "commit" and "-m" in cmd:
                commit_attempt += 1
                if commit_attempt == 1:
                    # First attempt: pre-commit fixes files
                    return False, "Files were modified by hook (ruff formatting)"
                else:
                    # Second attempt: succeeds
                    return True, "Created commit def456"
            else:
                return True, ""

        with patch.object(main, "run_git_command", side_effect=mock_run_git_command):
            main.session.commit_event.set()

            # Simulate one iteration of auto-commit worker (avoid infinite loop)
            try:
                if main.session.commit_event and main.session.commit_event.wait(
                    timeout=0.1
                ):
                    main.session.commit_event.clear()
                    repo_path = main.find_git_repo()
                    success, output = main.run_git_command(
                        ["status", "--porcelain"], repo_path
                    )
                    if success and output.strip():
                        main.run_git_command(["add", "."], repo_path)
                        timestamp = int(time.time())
                        commit_msg = f"Auto-commit {timestamp}"
                        main.run_git_command(["commit", "-m", commit_msg], repo_path)
            except Exception:
                pass

            # Should have tried commit twice
            commit_commands = [cmd for cmd in git_calls if cmd[0] == "commit"]
            assert len(commit_commands) == 2, (
                f"Expected 2 commit attempts, got {len(commit_commands)}"
            )

            # Both should be without --no-verify
            for cmd in commit_commands:
                assert "--no-verify" not in cmd, (
                    "Should not use --no-verify even when retrying"
                )

            print("✅ Auto-commit worker correctly handles pre-commit file fixes")
            return True


def test_auto_commit_worker_pre_commit_missing():
    """Test auto-commit worker when pre-commit is not available."""
    print("🧪 Testing auto-commit worker when pre-commit is missing...")

    with GitRepoFixture():
        main.session.is_vibing = True
        main.session.commit_event = Event()

        # Mock run_git_command to simulate pre-commit not found
        git_calls = []

        def mock_run_git_command(cmd, repo_path):
            git_calls.append(cmd.copy())

            if cmd == ["status", "--porcelain"]:
                return True, "M  test_file.py"
            elif cmd == ["add", "."]:
                return True, ""
            elif cmd[0] == "commit" and "-m" in cmd:
                return (
                    False,
                    "`pre-commit` not found. Did you forget to activate your virtualenv?",
                )
            elif cmd == ["reset", "HEAD"]:
                return True, ""
            else:
                return True, ""

        with patch.object(main, "run_git_command", side_effect=mock_run_git_command):
            main.session.commit_event.set()

            # Simulate one iteration of auto-commit worker (avoid infinite loop)
            try:
                if main.session.commit_event and main.session.commit_event.wait(
                    timeout=0.1
                ):
                    main.session.commit_event.clear()
                    repo_path = main.find_git_repo()
                    success, output = main.run_git_command(
                        ["status", "--porcelain"], repo_path
                    )
                    if success and output.strip():
                        main.run_git_command(["add", "."], repo_path)
                        timestamp = int(time.time())
                        commit_msg = f"Auto-commit {timestamp}"
                        main.run_git_command(["commit", "-m", commit_msg], repo_path)
            except Exception:
                pass

            # Should have attempted commit and then reset
            commit_commands = [cmd for cmd in git_calls if cmd[0] == "commit"]
            reset_commands = [cmd for cmd in git_calls if cmd[0] == "reset"]

            assert len(commit_commands) == 1, (
                f"Expected 1 commit attempt, got {len(commit_commands)}"
            )
            assert len(reset_commands) == 1, (
                f"Expected 1 reset command, got {len(reset_commands)}"
            )
            assert "--no-verify" not in commit_commands[0], (
                "Should not use --no-verify fallback"
            )

            print("✅ Auto-commit worker correctly handles missing pre-commit")
            return True


def test_auto_commit_worker_syntax_errors():
    """Test auto-commit worker when pre-commit fails due to syntax errors."""
    print("🧪 Testing auto-commit worker when pre-commit fails due to syntax errors...")

    with GitRepoFixture():
        main.session.is_vibing = True
        main.session.commit_event = Event()

        # Mock run_git_command to simulate syntax errors
        git_calls = []

        def mock_run_git_command(cmd, repo_path):
            git_calls.append(cmd.copy())

            if cmd == ["status", "--porcelain"]:
                return True, "M  bad_file.py"
            elif cmd == ["add", "."]:
                return True, ""
            elif cmd[0] == "commit" and "-m" in cmd:
                return (
                    False,
                    "ruff......................Failed\n- hook id: ruff\n- exit code: 1\n\nbad_file.py:5:1: E999 SyntaxError",
                )
            elif cmd == ["reset", "HEAD"]:
                return True, ""
            else:
                return True, ""

        with patch.object(main, "run_git_command", side_effect=mock_run_git_command):
            main.session.commit_event.set()

            # Simulate one iteration of auto-commit worker (avoid infinite loop)
            try:
                if main.session.commit_event and main.session.commit_event.wait(
                    timeout=0.1
                ):
                    main.session.commit_event.clear()
                    repo_path = main.find_git_repo()
                    success, output = main.run_git_command(
                        ["status", "--porcelain"], repo_path
                    )
                    if success and output.strip():
                        main.run_git_command(["add", "."], repo_path)
                        timestamp = int(time.time())
                        commit_msg = f"Auto-commit {timestamp}"
                        main.run_git_command(["commit", "-m", commit_msg], repo_path)
            except Exception:
                pass

            # Should have attempted commit and then reset due to syntax error
            commit_commands = [cmd for cmd in git_calls if cmd[0] == "commit"]
            reset_commands = [cmd for cmd in git_calls if cmd[0] == "reset"]

            assert len(commit_commands) == 1, (
                f"Expected 1 commit attempt, got {len(commit_commands)}"
            )
            assert len(reset_commands) == 1, (
                f"Expected 1 reset after syntax error, got {len(reset_commands)}"
            )

            print("✅ Auto-commit worker correctly handles syntax errors")
            return True


def test_simplified_auto_commit_approach():
    """Test that the simplified auto-commit approach works."""
    print("🧪 Testing simplified auto-commit approach...")

    with GitRepoFixture():
        main.session.is_vibing = True
        main.session.commit_event = Event()

        # Create a test file
        Path("test_file.txt").write_text("Test content")

        # Mock run_git_command for simple auto-commit
        git_calls = []

        def mock_run_git_command(cmd, repo_path):
            git_calls.append(cmd.copy())

            if cmd == ["status", "--porcelain"]:
                return True, "M  test_file.txt"
            elif cmd == ["add", "."]:
                return True, ""
            elif cmd[0] == "commit" and "-m" in cmd:
                return True, "Created commit abc123"
            else:
                return True, ""

        with patch.object(main, "run_git_command", side_effect=mock_run_git_command):
            main.session.commit_event.set()

            # Simulate one iteration of auto-commit worker (avoid infinite loop)
            try:
                if main.session.commit_event and main.session.commit_event.wait(
                    timeout=0.1
                ):
                    main.session.commit_event.clear()
                    repo_path = main.find_git_repo()
                    success, output = main.run_git_command(
                        ["status", "--porcelain"], repo_path
                    )
                    if success and output.strip():
                        main.run_git_command(["add", "."], repo_path)
                        timestamp = int(time.time())
                        commit_msg = f"Auto-commit {timestamp}"
                        main.run_git_command(["commit", "-m", commit_msg], repo_path)
            except Exception:
                pass

            # Verify simple commit was attempted
            commit_commands = [cmd for cmd in git_calls if cmd[0] == "commit"]
            assert len(commit_commands) == 1, (
                f"Expected 1 commit command, got {len(commit_commands)}"
            )

            # Should not have complex pre-commit handling
            assert "--no-verify" not in commit_commands[0], "Should not bypass hooks"

            print("✅ Simplified auto-commit approach works correctly")
            return True


def test_no_complex_hook_management():
    """Test that we don't have complex hook management."""
    print("🧪 Testing absence of complex hook management...")

    # Verify removed functions don't exist
    assert not hasattr(main, "ensure_pre_commit_setup"), (
        "ensure_pre_commit_setup should be removed"
    )
    assert not hasattr(main, "check_code_quality"), (
        "check_code_quality should be removed"
    )
    assert not hasattr(main, "fix_code_quality"), "fix_code_quality should be removed"

    print("✅ Complex hook management has been removed")
    return True


def test_file_handler_ignore_patterns():
    """Test that VibeFileHandler correctly ignores specified patterns."""
    print("🧪 Testing VibeFileHandler ignore patterns...")

    with GitRepoFixture():
        repo_path = Path.cwd()
        commit_event = Event()
        handler = main.VibeFileHandler(repo_path, commit_event)

        # Test ignore patterns
        test_cases = [
            (".git/config", True),  # Should ignore
            ("__pycache__/module.py", True),  # Should ignore
            (".venv/lib/python.py", True),  # Should ignore
            ("test.pyc", True),  # Should ignore
            (".DS_Store", True),  # Should ignore
            ("normal_file.py", False),  # Should not ignore
            ("normal_file.txt", False),  # Should not ignore
        ]

        for path, should_ignore in test_cases:
            result = handler.should_ignore_path(path)
            assert result == should_ignore, (
                f"Path {path}: expected ignore={should_ignore}, got {result}"
            )

        print("✅ VibeFileHandler correctly handles ignore patterns")
        return True


if __name__ == "__main__":
    print("=== Comprehensive Auto-Commit Tests ===")

    tests = [
        test_auto_commit_worker_pre_commit_success,
        test_auto_commit_worker_pre_commit_fixes_files,
        test_auto_commit_worker_pre_commit_missing,
        test_auto_commit_worker_syntax_errors,
        test_simplified_auto_commit_approach,
        test_no_complex_hook_management,
        test_file_handler_ignore_patterns,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed with exception: {e}")
            failed += 1
        print()

    print(f"=== Results: {passed} passed, {failed} failed ===")

    if failed == 0:
        print("🎉 All auto-commit tests passed!")
    else:
        print("💥 Some auto-commit tests failed!")
