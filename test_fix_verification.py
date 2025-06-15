#!/usr/bin/env python3
"""
Test to verify the PR creation bug fix works correctly.

This test verifies that:
1. run_command() works for both git and non-git commands
2. The fix properly calls gh pr create without prepending git
"""

import subprocess
import tempfile
import os
import sys

# Add current directory to path so we can import main
sys.path.insert(0, '.')
import main


def test_run_command_vs_run_git_command():
    """Test that run_command and run_git_command work as expected"""
    print("🧪 Testing run_command vs run_git_command...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        
        # Initialize git repo for testing
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)
        
        # Test run_git_command - should work for git commands
        print("1. Testing run_git_command with git status...")
        success, output = main.run_git_command(["status"])
        print(f"   Success: {success}, Output contains 'working tree': {'working tree' in output}")
        
        # Test run_command with git - should work the same way
        print("2. Testing run_command with git status...")
        success2, output2 = main.run_command(["git", "status"])
        print(f"   Success: {success2}, Output contains 'working tree': {'working tree' in output2}")
        
        # Test run_command with non-git command
        print("3. Testing run_command with echo...")
        success3, output3 = main.run_command(["echo", "hello world"])
        print(f"   Success: {success3}, Output: '{output3}'")
        
        # Test what would happen with the old bug
        print("4. Testing the old bug scenario (git gh pr create)...")
        success4, output4 = main.run_git_command(["gh", "pr", "create", "--help"])
        print(f"   Success: {success4} (should be False)")
        print(f"   Output contains 'unknown command': {'unknown command' in output4.lower()}")
        
        # Test the fix (gh pr create without git prefix)
        print("5. Testing the fix (gh pr create)...")
        success5, output5 = main.run_command(["gh", "pr", "create", "--help"])
        expected_success = subprocess.run(["which", "gh"], capture_output=True).returncode == 0
        print(f"   gh available: {expected_success}")
        if expected_success:
            print(f"   Success: {success5} (should be True if gh is available)")
            print(f"   Output contains 'create': {'create' in output5.lower()}")
        else:
            print("   gh not available, skipping test")
            
        return {
            "git_command_works": success,
            "run_command_git_works": success2,
            "run_command_echo_works": success3 and output3 == "hello world",
            "old_bug_fails": not success4,
            "new_fix_works": success5 if expected_success else True
        }


def test_pr_creation_code_analysis():
    """Analyze the fixed PR creation code"""
    print("\n🔍 Analyzing fixed stop_vibing() implementation...")
    
    # Use absolute path since we might be in a temp directory
    import os
    main_path = os.path.join(os.path.dirname(__file__), "main.py")
    with open(main_path, "r") as f:
        content = f.read()
    
    # Check for the fix
    if "run_command" in content and "gh" in content and "pr" in content and "create" in content:
        print("   ✅ Found run_command with gh pr create")
        
        # Look for the specific fixed line
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "run_command" in line and "gh" in line and "pr" in line and "create" in line:
                print(f"   Line {i + 1}: {line.strip()}")
                # Check it's not wrapped in run_git_command
                if "run_git_command" not in line:
                    print("   ✅ Uses run_command directly (not run_git_command)")
                    return True
                else:
                    print("   ❌ Still uses run_git_command wrapper")
                    return False
                    
    print("   ❌ Fix not found in code")
    return False


if __name__ == "__main__":
    print("Testing PR creation bug fix...\n")
    
    # Test the functions
    results = test_run_command_vs_run_git_command()
    
    # Test the code fix
    code_fixed = test_pr_creation_code_analysis()
    
    print(f"\n📊 Test Results:")
    for key, value in results.items():
        status = "✅" if value else "❌"
        print(f"   {status} {key}: {value}")
    
    print(f"   {'✅' if code_fixed else '❌'} code_properly_fixed: {code_fixed}")
    
    all_passed = all(results.values()) and code_fixed
    print(f"\n🎯 Overall: {'✅ All tests passed!' if all_passed else '❌ Some tests failed'}")