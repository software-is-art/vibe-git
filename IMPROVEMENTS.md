# vibe-git Improvements with beartype & plum

## Key Improvements Demonstrated

### 1. Runtime Type Safety with beartype

**Before:**
```python
def find_git_repo() -> Path:
    """Find the git repository root"""
    # No runtime validation that returned Path is actually a git repo
```

**After:**
```python
GitPath = Annotated[Path, Is[lambda p: (p / ".git").exists()]]

@beartype
def find_git_repo() -> GitPath:
    """Find the git repository root with type safety"""
    # beartype ensures returned Path has .git directory at runtime
```

### 2. Multiple Dispatch with plum

**Before:**
```python
def _start_vibing_impl() -> str:
    # 250+ lines of nested if/else logic handling different states
    if session.is_vibing:
        return "Already vibing!"
    
    # Check for uncommitted changes
    has_changes = ...
    if has_changes:
        return "Warning about changes..."
    
    # More branching logic...
```

**After:**
```python
@dispatch
def start_vibing_from_state(state: IdleState, repo_path: GitPath) -> str:
    """Clean state - start normally"""
    
@dispatch  
def start_vibing_from_state(state: VibingState, repo_path: GitPath) -> str:
    """Already vibing - return status"""
    
@dispatch
def start_vibing_from_state(state: DirtyState, repo_path: GitPath) -> str:
    """Dirty state - return instructions"""
```

### 3. Type-Safe State Machine

**Before:**
```python
@dataclass
class VibeSession:
    branch_name: str | None = None
    is_vibing: bool = False
    observer: Observer | None = None
    commit_event: Event | None = None
    # Multiple nullable fields, unclear valid combinations
```

**After:**
```python
@dataclass(frozen=True)
class IdleState:
    pass

@dataclass(frozen=True) 
class VibingState:
    branch_name: BranchName
    observer: Observer
    commit_event: Event
    # All fields required when vibing

SessionState = IdleState | VibingState | DirtyState

@dataclass
class VibeSession:
    state: SessionState = IdleState()
    
    @beartype
    def transition_to(self, new_state: SessionState) -> None:
        self.state = new_state
```

### 4. Semantic Types

**Before:**
```python
def get_current_branch(repo_path: Path) -> str | None:
    # Returns raw string, could be anything
```

**After:**
```python
BranchName = NewType("BranchName", str)
CommitHash = NewType("CommitHash", str)

@beartype
def get_current_branch(repo_path: GitPath) -> BranchName | None:
    # Clear semantic meaning, type-checked at runtime
```

### 5. Command Overloading

**Before:**
```python
def run_command(args: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    # Only accepts list of strings
```

**After:**
```python
@dispatch
def run_command(args: list[str], cwd: Path | None = None) -> CommandResult:
    """List version"""

@dispatch  
def run_command(command: str, cwd: Path | None = None) -> CommandResult:
    """String version - splits automatically"""
    return run_command(command.split(), cwd)
```

## Benefits

1. **Catch Bugs Earlier**: beartype catches type errors at runtime before they cause issues
2. **Cleaner Code**: plum dispatch eliminates deeply nested if/else chains
3. **Better Documentation**: Types serve as inline documentation
4. **Safer Refactoring**: Type system catches breaking changes
5. **Explicit States**: No more checking multiple boolean flags

## Migration Path

1. Add dependencies to pyproject.toml ✓
2. Gradually add @beartype decorators to existing functions
3. Replace complex branching logic with @dispatch
4. Convert implicit states to explicit state types
5. Add semantic types (NewType) for domain concepts