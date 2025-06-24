"""Tests for the main function"""

import signal
from unittest.mock import MagicMock, patch

from vibe_git.main import main, signal_handler


def test_main_function_runs():
    """Test that main function runs without errors"""
    # Mock the global mcp object
    with patch("vibe_git.main.mcp") as mock_mcp:
        # Mock signal.signal to prevent actual signal handling
        with patch("vibe_git.main.signal.signal") as mock_signal:
            # Test that main() runs without raising exceptions
            main()

            # Verify signal handlers were set up
            assert mock_signal.call_count == 2
            mock_signal.assert_any_call(signal.SIGINT, signal_handler)
            mock_signal.assert_any_call(signal.SIGTERM, signal_handler)

            # Verify run was called
            mock_mcp.run.assert_called_once()


def test_signal_handler():
    """Test that signal handler works correctly"""
    # Import VibingState to mock isinstance check
    from vibe_git.main import VibingState

    # Mock session and sys.exit
    with patch("vibe_git.main.session") as mock_session:
        with patch("vibe_git.main.sys.exit") as mock_exit:
            # Create a real VibingState instance with mock observer
            mock_observer = MagicMock()
            mock_event = MagicMock()
            vibing_state = VibingState(
                branch_name="vibe-test", observer=mock_observer, commit_event=mock_event
            )
            mock_session.state = vibing_state

            # Call signal handler
            signal_handler(signal.SIGINT, None)

            # Verify observer was stopped
            mock_observer.stop.assert_called_once()

            # Verify exit was called
            mock_exit.assert_called_once_with(0)


def test_main_integrates_with_fastmcp():
    """Test that main() properly integrates with FastMCP by checking module-level setup"""
    # Import the module to check that mcp is created properly
    import vibe_git.main as main_module

    # Verify mcp instance exists
    assert hasattr(main_module, "mcp")

    # Verify it's a FastMCP instance
    assert main_module.mcp.__class__.__name__ == "FastMCP"
