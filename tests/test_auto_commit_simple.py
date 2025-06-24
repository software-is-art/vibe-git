#!/usr/bin/env python3
"""
Simple tests for auto-commit mechanism improvements.
"""

from vibe_git import main


def test_auto_commit_worker_simplicity():
    """Test that auto_commit_worker is simple and focused."""
    import inspect

    source = inspect.getsource(main.auto_commit_worker)
    # Should be simple - just commit without complex hook management
    assert "commit" in source
    assert "timestamp" in source
    print("✅ auto_commit_worker is simple and focused")


def test_auto_commit_worker_function_exists():
    """Test that auto_commit_worker function exists."""
    assert hasattr(main, "auto_commit_worker")
    assert callable(main.auto_commit_worker)
    print("✅ auto_commit_worker function exists")


def test_no_verify_in_auto_commit():
    """Test that --no-verify IS used in auto-commit to prevent hook noise."""
    import inspect

    source = inspect.getsource(main.auto_commit_worker)
    assert "--no-verify" in source, (
        "auto_commit_worker should use --no-verify to prevent hook noise during vibe sessions"
    )
    print("✅ auto_commit_worker uses --no-verify to prevent hook noise")


def test_stop_vibing_respects_hooks():
    """Test that stop_vibing respects hooks on the final squashed commit."""
    import inspect

    source = inspect.getsource(main.stop_vibing.fn)
    # Should use --no-verify for squash, then amend without it
    assert "--no-verify" in source, "Should use --no-verify for initial squash"
    assert "amend" in source, "Should amend to run hooks"
    print("✅ stop_vibing respects hooks on final commit")


def test_file_handler_ignore_functionality():
    """Test VibeFileHandler ignore functionality."""
    import subprocess
    import tempfile
    from pathlib import Path
    from threading import Event

    # Create a temporary git repo for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)

        # Initialize git repo
        subprocess.run(["git", "init"], cwd=repo_path, capture_output=True)
        subprocess.run(
            ["git", "config", "user.name", "Test"], cwd=repo_path, capture_output=True
        )
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=repo_path,
            capture_output=True,
        )

        # Now repo_path is a valid GitPath
        from vibe_git.type_utils import GitPath

        repo_path = GitPath(repo_path)

        handler = main.VibeFileHandler(repo_path, Event())

        # Create a .gitignore file
        gitignore_content = "__pycache__/\n*.pyc\n.venv/\n"
        (repo_path / ".gitignore").write_text(gitignore_content)

        # Test some basic ignore patterns
        assert handler.should_ignore_path(".git/config")  # .git is always ignored
        assert handler.should_ignore_path("__pycache__/test.py")  # in .gitignore
        assert not handler.should_ignore_path("normal_file.py")  # not ignored

        print("✅ VibeFileHandler ignore functionality works")


if __name__ == "__main__":
    print("=== Simple Auto-Commit Tests ===")

    tests = [
        test_auto_commit_worker_simplicity,
        test_auto_commit_worker_function_exists,
        test_no_verify_in_auto_commit,
        test_stop_vibing_respects_hooks,
        test_file_handler_ignore_functionality,
    ]

    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}")
            exit(1)

    print("🎉 All simple tests passed!")
