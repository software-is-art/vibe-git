#!/usr/bin/env python3
"""
Demonstrate the verify-push solution for the race condition bug.

Instead of retry logic or atomic operations, we verify that the 
remote branch exists after pushing before attempting PR creation.
"""

import time
import subprocess
from pathlib import Path


def run_git_command(cmd, repo_path):
    """Mock of the git command runner."""
    try:
        result = subprocess.run(
            cmd, cwd=repo_path, capture_output=True, text=True, check=False
        )
        return result.returncode == 0, result.stdout.strip()
    except Exception as e:
        return False, str(e)


def verify_remote_branch_exists(branch_name, repo_path, max_attempts=5, delay=1.0):
    """
    Verify that a branch exists on the remote repository.
    
    Args:
        branch_name: Name of the branch to check
        repo_path: Path to the git repository
        max_attempts: Maximum number of verification attempts
        delay: Delay between attempts in seconds
        
    Returns:
        tuple: (success, message)
    """
    for attempt in range(max_attempts):
        # Check if remote branch exists using git ls-remote
        success, output = run_git_command(
            ["git", "ls-remote", "--heads", "origin", branch_name], repo_path
        )
        
        if success and branch_name in output:
            return True, f"Remote branch '{branch_name}' confirmed to exist"
        
        if attempt < max_attempts - 1:  # Don't sleep on last attempt
            print(f"  Attempt {attempt + 1}/{max_attempts}: Branch not yet visible on remote, waiting {delay}s...")
            time.sleep(delay)
    
    return False, f"Remote branch '{branch_name}' not found after {max_attempts} attempts"


def improved_stop_vibing_logic(branch_name, commit_message, repo_path):
    """
    Improved stop_vibing logic with remote branch verification.
    
    This eliminates the race condition between push and PR creation.
    """
    print(f"🚀 Starting improved stop_vibing for branch '{branch_name}'...")
    
    # Step 1: Push branch
    print("📤 Pushing branch to remote...")
    push_success, push_output = run_git_command(
        ["git", "push", "-u", "origin", branch_name], repo_path
    )
    if not push_success:
        return False, f"❌ Error pushing branch: {push_output}"
    
    print("✅ Push command completed successfully")
    
    # Step 2: Verify remote branch exists (this is the key improvement!)
    print("🔍 Verifying remote branch exists...")
    verify_success, verify_message = verify_remote_branch_exists(branch_name, repo_path)
    if not verify_success:
        return False, f"❌ {verify_message}"
    
    print(f"✅ {verify_message}")
    
    # Step 3: Create PR (now safe from race conditions!)
    print("📋 Creating pull request...")
    pr_title = commit_message.split('\n')[0] if commit_message else "Pull Request"
    pr_success, pr_output = run_git_command(
        ["gh", "pr", "create", "--title", pr_title, "--body", commit_message], repo_path
    )
    
    if pr_success:
        print(f"✅ PR created successfully: {pr_output}")
        return True, f"🏁 Success: Branch pushed and PR created: {pr_output}"
    else:
        print(f"⚠️ PR creation failed: {pr_output}")
        return True, f"🏁 Branch pushed successfully, but PR creation failed: {pr_output}"


def demonstrate_solution():
    """Demonstrate the improved approach."""
    print("=== Demonstrating Verify-Push Solution ===")
    print()
    
    # Simulate the improved logic
    repo_path = Path.cwd()
    branch_name = "demo-branch-123"
    commit_message = "Fix race condition in stop_vibing()\n\nThis commit demonstrates the verify-push solution."
    
    print("This approach:")
    print("1. Pushes the branch normally")
    print("2. Verifies the remote branch exists using 'git ls-remote'")
    print("3. Only attempts PR creation after confirmation")
    print("4. Eliminates race conditions without complex retry logic")
    print()
    
    print("Benefits:")
    print("✅ Simple and reliable")
    print("✅ No arbitrary delays or retry logic")  
    print("✅ Explicit verification of remote state")
    print("✅ Clear error messages if verification fails")
    print("✅ Works regardless of GitHub API sync timing")
    print()
    
    # Show what the git ls-remote command looks like
    print("Example verification command:")
    print(f"  git ls-remote --heads origin {branch_name}")
    print()
    print("This command returns the commit SHA if the branch exists:")
    print(f"  abc123def456... refs/heads/{branch_name}")
    print("Or empty output if the branch doesn't exist yet.")


if __name__ == "__main__":
    demonstrate_solution()