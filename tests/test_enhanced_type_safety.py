"""Tests for enhanced type safety features"""

import pytest
from beartype.roar import BeartypeCallHintViolation

from vibe_git.event_types import CommitEvent, StateTransitionEvent
from vibe_git.result_types import ChangesResult, CommandResult, ParsedMessage
from vibe_git.state_types import DirtyState, IdleState, VibingState
from vibe_git.state_utils import get_state_name, validate_state_transition
from vibe_git.type_utils import (
    NonEmptyString,
    ValidBranchName,
    ValidCommitMessage,
    ValidTimestamp,
    VibeBranchName,
    as_vibe_branch,
    is_vibe_branch,
)


class TestEnhancedTypes:
    """Test enhanced type definitions"""
    
    def test_non_empty_string_validation(self):
        """Test NonEmptyString validation"""
        from beartype import beartype
        
        @beartype
        def process_string(s: NonEmptyString) -> str:
            return s
        
        # Should work with valid strings
        assert process_string("hello") == "hello"
        
        # Should fail with empty string
        with pytest.raises(BeartypeCallHintViolation):
            process_string("")
            
        # Should fail with whitespace only
        with pytest.raises(BeartypeCallHintViolation):
            process_string("   ")
    
    def test_valid_branch_name(self):
        """Test ValidBranchName validation"""
        from beartype import beartype
        
        @beartype
        def process_branch(b: ValidBranchName) -> str:
            return b
        
        # Valid branch names
        assert process_branch("main") == "main"
        assert process_branch("feature/test-123") == "feature/test-123"
        assert process_branch("vibe-1234567") == "vibe-1234567"
        
        # Invalid branch names
        with pytest.raises(BeartypeCallHintViolation):
            process_branch("branch with spaces")
        
        with pytest.raises(BeartypeCallHintViolation):
            process_branch("branch@special")
    
    def test_vibe_branch_name(self):
        """Test VibeBranchName validation"""
        from beartype import beartype
        
        @beartype
        def process_vibe_branch(b: VibeBranchName) -> str:
            return b
        
        # Valid vibe branches
        assert process_vibe_branch("vibe-123") == "vibe-123"
        assert process_vibe_branch("vibe-feature") == "vibe-feature"
        
        # Invalid vibe branches
        with pytest.raises(BeartypeCallHintViolation):
            process_vibe_branch("main")
        
        with pytest.raises(BeartypeCallHintViolation):
            process_vibe_branch("feature-vibe")
    
    def test_as_vibe_branch(self):
        """Test as_vibe_branch converter"""
        # Valid conversion
        vibe = as_vibe_branch("vibe-123")
        assert vibe == "vibe-123"
        assert is_vibe_branch(vibe)
        
        # Invalid conversion
        with pytest.raises(ValueError, match="is not a vibe branch"):
            as_vibe_branch("main")
    
    def test_valid_timestamp(self):
        """Test ValidTimestamp validation"""
        from beartype import beartype
        
        @beartype
        def process_timestamp(t: ValidTimestamp) -> int:
            return t
        
        # Valid timestamps
        assert process_timestamp(1234567890) == 1234567890
        assert process_timestamp(1) == 1
        
        # Invalid timestamps
        with pytest.raises(BeartypeCallHintViolation):
            process_timestamp(0)
            
        with pytest.raises(BeartypeCallHintViolation):
            process_timestamp(-1)
    
    def test_valid_commit_message(self):
        """Test ValidCommitMessage validation"""
        from beartype import beartype
        
        @beartype
        def process_commit_msg(m: ValidCommitMessage) -> str:
            return m
        
        # Valid messages
        assert process_commit_msg("Fix bug") == "Fix bug"
        # Multi-line messages are OK if newline comes after 50 chars
        long_first_line = "A" * 51  # 51 chars, no newline in first 50
        assert process_commit_msg(long_first_line + "\nDetailed description") == long_first_line + "\nDetailed description"
        
        # Invalid - empty
        with pytest.raises(BeartypeCallHintViolation):
            process_commit_msg("")
        
        # Invalid - newline in first 50 chars
        with pytest.raises(BeartypeCallHintViolation):
            process_commit_msg("This is a\nvery long commit message that has newline")


class TestResultTypes:
    """Test result type dataclasses"""
    
    def test_command_result(self):
        """Test CommandResult with backwards compatibility"""
        result = CommandResult(success=True, output="test output")
        
        # Direct access
        assert result.success is True
        assert result.output == "test output"
        
        # Tuple unpacking
        success, output = result
        assert success is True
        assert output == "test output"
        
        # Indexing
        assert result[0] is True
        assert result[1] == "test output"
        
        # Index out of range
        with pytest.raises(IndexError):
            _ = result[2]
    
    def test_changes_result(self):
        """Test ChangesResult with backwards compatibility"""
        result = ChangesResult(has_changes=True, details="M file.py")
        
        # Direct access
        assert result.has_changes is True
        assert result.details == "M file.py"
        
        # Tuple unpacking
        has_changes, details = result
        assert has_changes is True
        assert details == "M file.py"
        
        # Indexing
        assert result[0] is True
        assert result[1] == "M file.py"
    
    def test_parsed_message(self):
        """Test ParsedMessage"""
        from vibe_git.type_utils import PRBody, PRTitle
        
        result = ParsedMessage(
            title=PRTitle("Fix bug"),
            body=PRBody("Fix bug\n\nDetailed description")
        )
        
        # Direct access
        assert result.title == "Fix bug"
        assert result.body == "Fix bug\n\nDetailed description"
        
        # Tuple unpacking
        title, body = result
        assert title == "Fix bug"
        assert body == "Fix bug\n\nDetailed description"


class TestStateUtils:
    """Test state machine utilities"""
    
    def test_get_state_name(self):
        """Test state name extraction"""
        assert get_state_name(IdleState()) == "idle"
        assert get_state_name(VibingState(
            branch_name="vibe-123",
            observer=None,  # type: ignore
            commit_event=None  # type: ignore
        )) == "vibing"
        assert get_state_name(DirtyState(
            branch_name="main",
            changes="M file.py"
        )) == "dirty"
    
    def test_valid_state_transitions(self):
        """Test valid state transitions"""
        idle = IdleState()
        vibing = VibingState(
            branch_name="vibe-123",
            observer=None,  # type: ignore
            commit_event=None  # type: ignore
        )
        dirty = DirtyState(branch_name="main", changes="M file.py")
        
        # Valid transitions from idle
        validate_state_transition(idle, vibing)  # No exception
        validate_state_transition(idle, dirty)   # No exception
        
        # Valid transition from vibing
        validate_state_transition(vibing, idle)  # No exception
        
        # Valid transitions from dirty
        validate_state_transition(dirty, idle)   # No exception
        validate_state_transition(dirty, vibing) # No exception
    
    def test_invalid_state_transitions(self):
        """Test invalid state transitions"""
        idle = IdleState()
        vibing = VibingState(
            branch_name="vibe-123",
            observer=None,  # type: ignore
            commit_event=None  # type: ignore
        )
        dirty = DirtyState(branch_name="main", changes="M file.py")
        
        # Invalid transitions
        with pytest.raises(ValueError, match="Invalid state transition"):
            validate_state_transition(idle, idle)
        
        with pytest.raises(ValueError, match="Invalid state transition"):
            validate_state_transition(vibing, vibing)
            
        with pytest.raises(ValueError, match="Invalid state transition"):
            validate_state_transition(vibing, dirty)


class TestEventTypes:
    """Test event type dataclasses"""
    
    def test_commit_event(self):
        """Test CommitEvent"""
        from datetime import datetime
        from pathlib import Path
        
        event = CommitEvent(
            timestamp=datetime.now(),
            files_changed=[Path("file1.py"), Path("file2.py")],
            branch_name="vibe-123"
        )
        
        assert event.has_changes is True
        assert len(event.files_changed) == 2
        
        # Empty event
        empty_event = CommitEvent(
            timestamp=datetime.now(),
            files_changed=[],
            branch_name="vibe-123"
        )
        assert empty_event.has_changes is False
    
    def test_state_transition_event(self):
        """Test StateTransitionEvent"""
        from datetime import datetime
        from vibe_git.state_types import SessionState
        
        event = StateTransitionEvent(
            from_state=IdleState,
            to_state=VibingState,
            timestamp=datetime.now(),
            reason="User started vibing"
        )
        
        assert event.state_changed is True
        
        # No change event
        no_change = StateTransitionEvent(
            from_state=IdleState,
            to_state=IdleState,
            timestamp=datetime.now()
        )
        assert no_change.state_changed is False