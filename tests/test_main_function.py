"""Tests for the main function"""

from unittest.mock import patch, MagicMock, call

import pytest

from vibe_git.main import main


def test_main_function_runs():
    """Test that main function runs without errors"""
    # Mock the MCP server
    mock_mcp = MagicMock()
    
    # Mock the FastMCP class
    with patch('vibe_git.main.FastMCP') as mock_fastmcp_class:
        # Configure the mock to return our mock_mcp instance
        mock_fastmcp_class.return_value = mock_mcp
        
        # Test that main() runs without raising exceptions
        # Call main - it should set up the server
        main()
        
        # Verify FastMCP was called with correct parameters
        mock_fastmcp_class.assert_called_once_with(
            "vibe-git",
            dependencies=["git", "gh"]
        )
        
        # Verify tools were registered
        assert mock_mcp.tool.call_count >= 6  # We have 6 tools
        
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
        try:
            main()
        except KeyboardInterrupt:
            # Should not re-raise KeyboardInterrupt
            pytest.fail("main() should handle KeyboardInterrupt gracefully")
        except SystemExit:
            # SystemExit is okay
            pass


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
        
        try:
            main()
        except SystemExit:
            pass
        
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