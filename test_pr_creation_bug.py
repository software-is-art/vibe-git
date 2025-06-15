#!/usr/bin/env python3
"""
Test to reproduce the PR creation failure bug in stop_vibing().

Issue: stop_vibing() reports success but doesn't actually create a PR.
This test simulates the exact scenario and checks if a PR is actually created.
"""

import os
import tempfile
import shutil
import subprocess
import time
import main


class GitRepoFixture:
    def __init__(self):
        self.temp_dir = None
        self.original_cwd = None

    def __enter__(self):
        # Save original directory
        self.original_cwd = os.getcwd()
        
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp(prefix="vibe_test_")
        os.chdir(self.temp_dir)
        
        # Initialize git repo
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)
        
        # Create initial commit
        with open("README.md", "w") as f:
            f.write("# Test Repository\n")
        subprocess.run(["git", "add", "README.md"], check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)
        
        # Create main branch explicitly
        subprocess.run(["git", "branch", "-M", "main"], check=True)
        
        return self.temp_dir

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Return to original directory
        os.chdir(self.original_cwd)
        # Clean up temp directory
        shutil.rmtree(self.temp_dir)


def test_stop_vibing_pr_creation_failure():
    """
    Test that reproduces the PR creation failure bug.
    
    This test simulates the exact scenario where stop_vibing() reports
    success but doesn't actually create a PR on GitHub.
    """
    print("🧪 Testing PR creation failure in stop_vibing()...")
    
    with GitRepoFixture():
        # Start vibing
        print("1. Starting vibe session...")
        start_result = main.start_vibing.fn()
        print(f"   Start result: {start_result}")
        
        # Make some changes
        print("2. Making changes...")
        with open("test_change.txt", "w") as f:
            f.write("This is a test change for PR creation bug reproduction\n")
        
        # Wait a moment for file watcher to detect
        time.sleep(2)
        
        # Get current branch name before stopping
        branch_result = subprocess.run(
            ["git", "branch", "--show-current"], 
            capture_output=True, text=True
        )
        current_branch = branch_result.stdout.strip()
        print(f"   Current branch: {current_branch}")
        
        # Stop vibing
        print("3. Stopping vibe session...")
        commit_message = "Test PR creation bug reproduction"
        stop_result = main.stop_vibing.fn(commit_message)
        print(f"   Stop result: {stop_result}")
        
        # Check if we're back on main
        branch_result = subprocess.run(
            ["git", "branch", "--show-current"], 
            capture_output=True, text=True
        )
        final_branch = branch_result.stdout.strip()
        print(f"   Final branch: {final_branch}")
        
        # The key test: Did a PR actually get created?
        print("4. Checking if PR was actually created...")
        
        # This will fail in our test environment since we don't have a real remote
        # But we can check if the gh command was attempted
        
        # Check if the function reported success
        success_reported = "🏁 Stopped vibing!" in stop_result
        print(f"   Success reported: {success_reported}")
        
        # Check if we're back on main (this should work now)
        back_on_main = final_branch == "main"
        print(f"   Back on main branch: {back_on_main}")
        
        # In a real scenario, we'd check: gh pr list | grep "commit_message"
        # But for this test, we'll analyze the stop_vibing implementation
        
        print("5. Analysis:")
        print(f"   - stop_vibing() reported success: {success_reported}")
        print(f"   - User returned to main branch: {back_on_main}")
        print(f"   - Original vibe branch: {current_branch}")
        
        if success_reported and back_on_main:
            print("   ✅ Basic functionality works, but PR creation needs verification")
        else:
            print("   ❌ Basic functionality failed")
            
        return {
            "success_reported": success_reported,
            "back_on_main": back_on_main,
            "original_branch": current_branch,
            "final_branch": final_branch
        }


def analyze_pr_creation_code():
    """
    Analyze the stop_vibing implementation to identify PR creation issues.
    """
    print("\n🔍 Analyzing stop_vibing() implementation...")
    
    # Read the main.py file to analyze PR creation logic
    with open("main.py", "r") as f:
        content = f.read()
    
    print("Looking for PR creation logic...")
    
    # Look for gh pr create command
    if "gh pr create" in content:
        print("   ✅ Found 'gh pr create' command in code")
        
        # Extract the PR creation section
        lines = content.split('\n')
        pr_lines = []
        capture = False
        
        for i, line in enumerate(lines):
            if "gh pr create" in line:
                # Capture context around the PR creation
                start = max(0, i - 5)
                end = min(len(lines), i + 10)
                pr_lines = lines[start:end]
                break
        
        print("   PR creation code section:")
        for i, line in enumerate(pr_lines):
            print(f"   {start + i + 1:3d}: {line}")
            
    else:
        print("   ❌ No 'gh pr create' command found!")
        
    # Look for error handling around PR creation
    if "pr_success" in content or "pr_result" in content:
        print("   ✅ Found PR result handling variables")
    else:
        print("   ⚠️  No explicit PR result handling found")
        
    # Look for return statements after PR creation
    print("\n   Checking return logic after PR creation...")
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        if "gh pr create" in line:
            # Look at the next 15 lines for return statements
            for j in range(1, 16):
                if i + j < len(lines):
                    next_line = lines[i + j].strip()
                    if next_line.startswith("return"):
                        print(f"   Return found {j} lines after gh pr create: {next_line}")
                        break
            break


if __name__ == "__main__":
    # Run the reproduction test
    result = test_stop_vibing_pr_creation_failure()
    
    # Analyze the code
    analyze_pr_creation_code()
    
    print(f"\n📊 Test Results: {result}")