#!/usr/bin/env python3
"""
Simple tests for auto-commit mechanism improvements.
"""

import main


def test_ensure_pre_commit_setup_function_exists():
    """Test that ensure_pre_commit_setup function exists."""
    assert hasattr(main, "ensure_pre_commit_setup")
    assert callable(main.ensure_pre_commit_setup)
    print("✅ ensure_pre_commit_setup function exists")


def test_auto_commit_worker_function_exists():
    """Test that auto_commit_worker function exists."""
    assert hasattr(main, "auto_commit_worker")
    assert callable(main.auto_commit_worker)
    print("✅ auto_commit_worker function exists")


def test_no_verify_not_in_auto_commit():
    """Test that --no-verify is not used in auto-commit code."""
    import inspect

    source = inspect.getsource(main.auto_commit_worker)
    assert "--no-verify" not in source, "auto_commit_worker should not use --no-verify"
    print("✅ auto_commit_worker does not use --no-verify")


def test_pre_commit_error_handling():
    """Test that pre-commit error handling is in place."""
    import inspect

    source = inspect.getsource(main.auto_commit_worker)
    assert "pre-commit` not found" in source, "Should check for pre-commit not found"
    assert "reset" in source.lower(), "Should reset changes on pre-commit failure"
    print("✅ Pre-commit error handling is present")


def test_file_handler_ignore_functionality():
    """Test VibeFileHandler ignore functionality."""
    from pathlib import Path
    from threading import Event

    handler = main.VibeFileHandler(Path("."), Event())

    # Test some basic ignore patterns
    assert handler.should_ignore_path(".git/config")
    assert handler.should_ignore_path("__pycache__/test.py")
    assert not handler.should_ignore_path("normal_file.py")

    print("✅ VibeFileHandler ignore functionality works")


if __name__ == "__main__":
    print("=== Simple Auto-Commit Tests ===")

    tests = [
        test_ensure_pre_commit_setup_function_exists,
        test_auto_commit_worker_function_exists,
        test_no_verify_not_in_auto_commit,
        test_pre_commit_error_handling,
        test_file_handler_ignore_functionality,
    ]

    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}")
            exit(1)

    print("🎉 All simple tests passed!")
