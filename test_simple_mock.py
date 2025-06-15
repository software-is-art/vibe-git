#!/usr/bin/env python3
"""
Simple test to verify our mocking approach works.
"""

from unittest.mock import patch
import main

def test_simple_mock():
    """Test that we can mock run_git_command successfully."""
    
    def mock_run_git_command(cmd, repo_path):
        print(f"MOCK CALLED: {cmd}")
        if cmd[0] == "git" and cmd[1] == "checkout":
            return False, "Mock checkout failure"
        return True, "Mock success"
    
    # Test that the mock works
    with patch.object(main, 'run_git_command', side_effect=mock_run_git_command):
        success, output = main.run_git_command(["git", "checkout", "main"], "/tmp")
        print(f"Result: success={success}, output='{output}'")
        assert not success
        assert "Mock checkout failure" in output
    
    print("✅ Mock verification successful!")

if __name__ == "__main__":
    test_simple_mock()