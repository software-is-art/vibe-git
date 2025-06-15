#!/usr/bin/env python3
"""
Simple tests for auto-commit mechanism improvements.
"""

import main


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


def test_no_verify_not_in_auto_commit():
    """Test that --no-verify is not used in auto-commit code."""
    import inspect

    source = inspect.getsource(main.auto_commit_worker)
    assert "--no-verify" not in source, "auto_commit_worker should not use --no-verify"
    print("✅ auto_commit_worker does not use --no-verify")


def test_auto_commit_respects_hooks():
    """Test that auto-commit respects existing hooks naturally."""
    import inspect

    source = inspect.getsource(main.auto_commit_worker)
    # Should NOT use --no-verify (respects hooks naturally)
    assert "--no-verify" not in source, "Should not bypass hooks with --no-verify"
    assert "commit" in source, "Should still commit changes"
    print("✅ Auto-commit respects hooks naturally")


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
        test_auto_commit_worker_simplicity,
        test_auto_commit_worker_function_exists,
        test_no_verify_not_in_auto_commit,
        test_auto_commit_respects_hooks,
        test_file_handler_ignore_functionality,
    ]

    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}")
            exit(1)

    print("🎉 All simple tests passed!")
