#!/usr/bin/env python3
"""
Refined test for Case 4: Final checkout failure handling.

This test specifically targets the final checkout to main (line 367 in main.py)
and verifies that errors are properly caught and reported.
"""

import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import main


class GitRepoFixture:
    """Helper class to create temporary git repositories for testing"""
    
    def __init__(self):
        self.temp_dir = None
        self.original_cwd = None
        self.repo_path = None
        
    def __enter__(self):
        self.original_cwd = os.getcwd()
        self.temp_dir = tempfile.mkdtemp(prefix="vibe_git_test_")
        self.repo_path = Path(self.temp_dir)
        
        os.chdir(self.temp_dir)
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "config", "init.defaultBranch", "main"], check=True)
        
        (self.repo_path / "README.md").write_text("# Test Repository")
        subprocess.run(["git", "add", "README.md"], check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)
        
        self.remote_dir = tempfile.mkdtemp(prefix="vibe_git_remote_")
        subprocess.run(["git", "init", "--bare", self.remote_dir], check=True)
        subprocess.run(["git", "remote", "add", "origin", self.remote_dir], check=True)
        subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
        
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.original_cwd:
            os.chdir(self.original_cwd)
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        if hasattr(self, 'remote_dir') and os.path.exists(self.remote_dir):
            shutil.rmtree(self.remote_dir, ignore_errors=True)


def test_final_checkout_failure_refined():
    """
    Refined test for case 4: Final checkout to main fails.
    
    This test uses a more sophisticated approach to target only the final checkout
    by tracking the complete sequence of git operations.
    """
    with GitRepoFixture():
        # Start vibe session
        result = main.start_vibing.fn()
        assert "Started vibing" in result or "vibing" in result.lower()
        
        # Make some changes
        Path("test_final_checkout.txt").write_text("Testing final checkout failure")
        time.sleep(2)  # Wait for auto-commit
        
        # Track all git operations to identify the final checkout
        original_run_git_command = main.run_git_command
        git_calls = []
        
        def mock_run_git_command(cmd, repo_path):
            # Record all git calls
            git_calls.append(cmd.copy())
            
            # If this is a checkout command, analyze the pattern
            if cmd[0] == "git" and cmd[1] == "checkout" and cmd[2] == "main":
                print(f"DEBUG: Checkout to main #{len([c for c in git_calls if c[:3] == ['git', 'checkout', 'main']])}")
                
                # Look for the pattern that indicates this is the final checkout
                # The final checkout happens after PR creation (gh command)
                has_gh_command = any(c[0] == "gh" for c in git_calls)
                has_push_command = any(c[:2] == ['git', 'push'] for c in git_calls)
                
                print(f"DEBUG: has_gh_command={has_gh_command}, has_push_command={has_push_command}")
                print(f"DEBUG: Recent commands: {git_calls[-3:] if len(git_calls) >= 3 else git_calls}")
                
                # The final checkout happens after push and gh commands
                if has_gh_command and has_push_command:
                    print("DEBUG: This is the FINAL checkout - simulating failure")
                    return False, "Error: Unable to checkout main - working tree has staged changes"
                else:
                    print("DEBUG: Not the final checkout, letting it proceed")
            
            # All other commands work normally
            return original_run_git_command(cmd, repo_path)
        
        with patch.object(main, 'run_git_command', side_effect=mock_run_git_command):
            result = main.stop_vibing.fn(
                "Test final checkout failure - refined\n\nThis should catch the final checkout failure properly"
            )
            
            print(f"\nGit commands executed: {len(git_calls)}")
            for i, cmd in enumerate(git_calls):
                print(f"  {i+1}. {' '.join(cmd)}")
            
            print(f"\nResult: {result}")
            
            # The function should report the final checkout failure explicitly
            if "Error switching back to main" in result:
                print("✅ SUCCESS: Final checkout failure properly caught and reported!")
                assert "working tree has staged changes" in result
                return True
            else:
                print("❌ FAILURE: Final checkout failure not caught")
                print(f"Expected 'Error switching back to main', got: {result}")
                return False


def test_final_checkout_success_verification():
    """
    Verify that when final checkout succeeds, everything works as expected.
    """
    with GitRepoFixture():
        # Start vibe session
        result = main.start_vibing.fn()
        assert "Started vibing" in result or "vibing" in result.lower()
        
        # Make some changes
        Path("test_final_checkout_success.txt").write_text("Testing final checkout success")
        time.sleep(2)  # Wait for auto-commit
        
        # Don't mock anything - let it run normally
        result = main.stop_vibing.fn(
            "Test final checkout success\n\nThis should succeed and return to main"
        )
        
        print(f"Success case result: {result}")
        
        # Should report success
        assert "Stopped vibing" in result
        assert "Error" not in result
        
        # Should be on main branch
        current_branch = subprocess.run(
            ["git", "branch", "--show-current"], capture_output=True, text=True
        ).stdout.strip()
        assert current_branch == "main", f"Expected main, got {current_branch}"
        
        print("✅ SUCCESS: Normal case works correctly!")
        return True


if __name__ == "__main__":
    print("=== Testing final checkout failure (refined) ===")
    failure_test_passed = test_final_checkout_failure_refined()
    
    print("\n=== Testing final checkout success case ===")
    success_test_passed = test_final_checkout_success_verification()
    
    if failure_test_passed and success_test_passed:
        print("\n🎉 All refined tests passed!")
    else:
        print("\n💥 Some tests failed - need further investigation")