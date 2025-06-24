"""Tests for the main function"""

from unittest.mock import patch, MagicMock, call
import signal

import pytest

from vibe_git.main import main, signal_handler


def test_main_function_runs():
    """Test that main function runs without errors"""
    # Mock the global mcp object
    with patch('vibe_git.main.mcp') as mock_mcp:
        # Mock signal.signal to prevent actual signal handling
        with patch('vibe_git.main.signal.signal') as mock_signal:
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
    # Mock session and sys.exit
    with patch('vibe_git.main.session') as mock_session:
        with patch('vibe_git.main.sys.exit') as mock_exit:
            # Create a mock VibingState with observer
            mock_observer = MagicMock()
            mock_vibing_state = MagicMock()
            mock_vibing_state.observer = mock_observer
            mock_session.state = mock_vibing_state
            
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
    assert hasattr(main_module, 'mcp')
    
    # Verify it's a FastMCP instance
    assert main_module.mcp.__class__.__name__ == 'FastMCP'