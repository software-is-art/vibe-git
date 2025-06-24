"""Manual test to verify mutation detection"""
import tempfile
from pathlib import Path

# Create a test directory with only .GIT (uppercase)
with tempfile.TemporaryDirectory() as tmpdir:
    tmp_path = Path(tmpdir)
    
    # Create .GIT directory
    (tmp_path / ".GIT").mkdir()
    
    # Check both exist
    print(f".GIT exists: {(tmp_path / '.GIT').exists()}")
    print(f".git exists: {(tmp_path / '.git').exists()}")
    
    # Original code checks for .git
    original_check = (tmp_path / ".git").exists()
    print(f"Original check (.git): {original_check}")
    
    # Mutated code would check for .GIT
    mutated_check = (tmp_path / ".GIT").exists()
    print(f"Mutated check (.GIT): {mutated_check}")
    
    # If results differ, the mutation is detectable
    print(f"Mutation detectable: {original_check != mutated_check}")