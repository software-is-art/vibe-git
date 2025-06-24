# Type Safety Improvement Opportunities Report

## Overview
This report identifies opportunities to improve type safety in the vibe-git codebase using `@beartype` decorators and `@dispatch` from plum.

## Implementation Status
✅ = Implemented in this session
📋 = Documented for future implementation

## 1. Functions Missing @beartype Decorator

### src/vibe_git/vibe_status_only.py
- ✅ Fixed: `find_git_repo()` - Added @beartype
- ✅ Fixed: `run_git_command()` - Added @beartype  
- ✅ Fixed: `vibe_status()` - Added @beartype

### src/vibe_git/type_utils.py
- ✅ Fixed: `is_vibe_branch()` - Added @beartype
- ✅ Fixed: `validate_git_path()` - Added @beartype

### src/vibe_git/state_persistence.py
- ✅ Fixed: All methods in `SessionPersistence` class - Added @beartype to:
  - `__init__()`
  - `save_session()`
  - `load_session()`
  - `delete_session()`
  - `append_event()`
  - `has_session()`
  - `get_session_age_seconds()`
  - `is_session_stale()`

### src/vibe_git/main.py
- `main()` function (line 887) - Could benefit from @beartype
- `signal_handler()` (line 879) - Already has @beartype ✓

## 2. Functions with Complex Branching That Could Use @dispatch

### src/vibe_git/main.py
**Already using dispatch well for:**
- ✓ `run_command()` - String vs list[str] overloads
- ✓ `start_vibing_from_state()` - Different state types
- ✓ `_check_ignore()` in VibeFileHandler - String vs Path

**Opportunities for new dispatch usage:**
- `parse_commit_message()` (line 534) - Could have overloads for different input formats
- `ensure_on_main_branch()` (line 352) - Could dispatch on different branch naming strategies

### src/vibe_git/git_utils.py
**Already using dispatch for:**
- ✓ `run_command()` - String vs list[str] overloads

**New opportunities:**
- `checkout_branch()` (line 81) - Could dispatch on str vs BranchName types
- `create_branch()` (line 90) - Could dispatch on str vs BranchName types

## 3. Manual Type Checking That beartype Could Handle

### src/vibe_git/main.py
- Lines 439-459: Checking for uncommitted changes could be encapsulated with validated types
- Line 237: `is_vibe_branch()` does manual string checking that could be a validated type

### src/vibe_git/state_persistence.py
- Line 65-70: Manual JSON validation that could use beartype validators
- Line 96-101: Manual datetime parsing that could use validated types

## 4. Functions with Optional Parameters for Dispatch

### src/vibe_git/git_utils.py
- `get_current_branch(repo_path: GitPath | None = None)` - Could have two dispatched versions
- `has_uncommitted_changes(repo_path: GitPath | None = None)` - Could have two dispatched versions
- `checkout_branch(..., repo_path: GitPath | None = None)` - Could have overloads
- `create_branch(..., repo_path: GitPath | None = None)` - Could have overloads
- `ensure_on_main_branch(repo_path: GitPath | None = None)` - Could have overloads

## 5. validate_* Functions That Could Be beartype Validators

### src/vibe_git/type_utils.py
- `validate_git_path()` - Already exists but could be enhanced with Annotated types

**Potential new validators:**
```python
# Branch name validator
ValidBranchName = Annotated[str, Is[lambda s: bool(re.match(r'^[a-zA-Z0-9_\-./]+$', s))]]

# Non-empty string validator (already defined in main.py but not in type_utils)
NonEmptyString = Annotated[str, Is[lambda s: len(s.strip()) > 0]]

# Timestamp validator
ValidTimestamp = Annotated[int, Is[lambda t: t > 0]]

# Commit message validator
ValidCommitMessage = Annotated[str, Is[lambda s: len(s.strip()) > 0 and '\n' not in s.strip()[:50]]]
```

## 6. Functions Returning Tuples That Could Be More Strictly Typed

### Current tuple returns that could be NamedTuples or dataclasses:
- `run_command()` returns `tuple[bool, str]` - Could be `CommandResult` dataclass
- `has_uncommitted_changes()` returns `tuple[bool, str]` - Could be `ChangesResult` dataclass
- `parse_commit_message()` returns `tuple[PRTitle, PRBody]` - Could be `ParsedMessage` dataclass

### Suggested improvements:
```python
@dataclass
class CommandResult:
    success: bool
    output: str
    
@dataclass  
class ChangesResult:
    has_changes: bool
    details: str
    
@dataclass
class ParsedMessage:
    title: PRTitle
    body: PRBody
```

## 7. Functions Taking Union Types That Could Use Dispatch

### src/vibe_git/git_utils.py
- `checkout_branch(branch: str | BranchName, ...)` - Perfect for dispatch
- `create_branch(branch: str | BranchName, ...)` - Perfect for dispatch

### src/vibe_git/main.py
- `run_command(args: list[str], cwd: Path | None = None)` - Already using dispatch ✓
- Line 215: `get_current_branch()` returns `BranchName | None` - Could have type-safe handling

## 8. Additional Type Safety Improvements

### Semantic Types to Add
```python
# In type_utils.py
MainBranchName = Literal["main", "master"]
FilePattern = NewType("FilePattern", str)  # For glob patterns
GitRemote = NewType("GitRemote", str)  # For remote names like "origin"
RelativePath = Annotated[Path, Is[lambda p: not p.is_absolute()]]
```

### State Machine Improvements
The state machine pattern in main.py is excellent but could benefit from:
- Exhaustiveness checking with typing.assert_never
- More granular state transitions with validated preconditions

### Event Types
The Event objects could be more strictly typed:
```python
@dataclass
class CommitEvent:
    timestamp: CommitTimestamp
    files_changed: list[Path]
    
@dataclass
class StateTransitionEvent:
    from_state: type[SessionState]
    to_state: type[SessionState]
    timestamp: datetime
```

## Summary

### Completed in This Session ✅

1. **Added @beartype decorators to all missing functions:**
   - `vibe_status_only.py`: All functions now have @beartype
   - `type_utils.py`: Helper functions now have @beartype
   - `state_persistence.py`: All class methods now have @beartype
   - `main.py`: Added @beartype to main() function

2. **Enhanced type definitions with semantic validators:**
   - Added `ValidBranchName`, `NonEmptyString`, `ValidTimestamp`, `ValidCommitMessage`
   - Added `VibeBranchName` for vibe-specific branches
   - Added `MainBranchName`, `FilePattern`, `GitRemote`, `RelativePath`

3. **Implemented dispatch overloads for optional parameters:**
   - `git_utils.py`: All functions with optional `repo_path` now have dispatch overloads
   - Separate implementations for with/without repo_path parameters

4. **Created structured result types:**
   - `result_types.py`: CommandResult, ChangesResult, ParsedMessage dataclasses
   - Backward compatible with tuple unpacking

5. **Added comprehensive event types:**
   - `event_types.py`: Type-safe event classes for all system events
   - `state_types.py`: Extracted state types to avoid circular imports
   - `state_utils.py`: State machine utilities with exhaustiveness checking

6. **Comprehensive test coverage:**
   - `test_enhanced_type_safety.py`: Tests for all new type safety features
   - Validates beartype enforcement at runtime

### Future Improvements 📋

1. **Update main.py to use new result types** instead of tuples
2. **Add more semantic validators** for git-specific constraints
3. **Implement type-safe git command builders**
4. **Add property-based testing** with hypothesis for type validators
5. **Create type stubs** (.pyi files) for better IDE support

The codebase now has significantly enhanced type safety with runtime validation, making it more robust and self-documenting.