"""Tests for the main function"""

from unittest.mock import patch, MagicMock, call
import signal

import pytest

from vibe_git.main import main


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


def test_main_function_with_interrupt():
    """Test that main function handles keyboard interrupt gracefully"""
    # Mock the MCP server
    mock_mcp = MagicMock()
    
    # Make run() raise KeyboardInterrupt
    mock_mcp.run.side_effect = KeyboardInterrupt()
    
    # Mock the FastMCP class
    with patch('vibe_git.main.FastMCP') as mock_fastmcp_class:
        # Configure the mock to return our mock_mcp instance
        mock_fastmcp_class.return_value = mock_mcp
        
        # Test that main() handles KeyboardInterrupt without crashing
        # main() should handle KeyboardInterrupt gracefully
        main()  # Should not raise


def test_main_function_registers_all_tools():
    """Test that all expected tools are registered"""
    # Mock the MCP server
    mock_mcp = MagicMock()
    
    # Track registered tools
    registered_tools = []
    
    def track_tool_registration(func):
        registered_tools.append(func.__name__)
        return func
    
    mock_mcp.tool.side_effect = track_tool_registration
    
    # Mock the FastMCP class
    with patch('vibe_git.main.FastMCP') as mock_fastmcp_class:
        # Configure the mock to return our mock_mcp instance
        mock_fastmcp_class.return_value = mock_mcp
        
        main()
        
        # Verify all expected tools were registered
        expected_tools = [
            "start_vibing",
            "stop_vibing", 
            "vibe_status",
            "stash_and_vibe",
            "commit_and_vibe",
            "vibe_from_here"
        ]
        
        for tool in expected_tools:
            assert tool in registered_tools, f"Tool {tool} was not registered"