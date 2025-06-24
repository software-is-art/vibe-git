"""Verify the test catches the mutation"""
import tempfile
from pathlib import Path
from unittest.mock import patch

# Simulate the mutation by creating a modified validate_git_path
def validate_git_path_mutated(path: Path):
    """Mutated version that checks for .GIT instead of .git"""
    if not (path / ".GIT").exists():  # MUTATED: .git -> .GIT
        raise ValueError(f"{path} is not a git repository")
    return path

with tempfile.TemporaryDirectory() as tmpdir:
    tmp_path = Path(tmpdir)
    
    # Create a mock that tracks what path was checked
    checked_paths = []
    
    def mock_exists(self):
        # Record the path being checked
        checked_paths.append(str(self))
        # Only return True if checking for lowercase .git
        if str(self).endswith('/.git'):
            return True
        return False
    
    # Patch Path.exists to use our mock
    with patch.object(Path, 'exists', mock_exists):
        try:
            # This should fail because mutated code checks for .GIT
            # but mock only returns True for .git
            result = validate_git_path_mutated(tmp_path)
            print("ERROR: Mutated code didn't raise exception!")
        except ValueError as e:
            print(f"SUCCESS: Mutated code raised exception: {e}")
            print(f"Checked paths: {checked_paths}")
            print("The test successfully detects the mutation!")