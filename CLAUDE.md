# vibe-git MCP Server

## Project Overview
An MCP (Model Context Protocol) server that enables friction-free git workflows for "vibe coding" - allowing developers to focus on code while git operations happen automatically in the background.

## Core Functionality
- `start_vibing`: Creates a new branch and auto-commits all changes every second
- `stop_vibing`: Squashes commits, rebases on main, and creates a PR

## Architecture Decisions

### Language: Python
We're using Python with advanced type safety libraries for reliability and maintainability.

### Type Safety with beartype & plum
This project uses runtime type checking and multiple dispatch to achieve type safety similar to statically typed languages.

#### State Machine with Type Safety:
```python
# Vibe session states
@dataclass(frozen=True)
class IdleState:
    """No active vibe session"""
    pass

@dataclass(frozen=True)
class VibingState:
    """Active vibe session"""
    branch_name: BranchName
    observer: Observer
    commit_event: Event

@dataclass(frozen=True)
class DirtyState:
    """Repository has uncommitted changes"""
    branch_name: str
    changes: str
```

#### Multiple Dispatch for Clean Code:
```python
@dispatch
def start_vibing_from_state(state: IdleState, repo_path: GitPath) -> VibeStartResult:
    """Start from clean state"""

@dispatch  
def start_vibing_from_state(state: VibingState, repo_path: GitPath) -> VibeStartResult:
    """Already vibing"""

@dispatch
def start_vibing_from_state(state: DirtyState, repo_path: GitPath) -> VibeStartResult:
    """Handle uncommitted changes"""
```

#### Semantic Types with Runtime Validation:
```python
# Path that must contain .git directory
GitPath = Annotated[Path, Is[lambda p: (p / ".git").exists()]]

# Semantic string types
BranchName = NewType("BranchName", str)
CommitHash = NewType("CommitHash", str)
PRTitle = NewType("PRTitle", str)
```

#### Key Benefits:
1. **Runtime guarantees**: Invalid types caught before causing issues
2. **Clean dispatch**: No nested if/else chains
3. **Self-documenting**: Types express intent clearly
4. **State safety**: Invalid state transitions prevented
5. **Better refactoring**: Type system catches breaking changes

### Dependencies
- `fastmcp`: FastMCP framework for MCP protocol implementation
- `watchdog`: Cross-platform file system monitoring
- `beartype`: Runtime type checking and validation
- `plum-dispatch`: Multiple dispatch for clean code organization
- `pydantic`: Data validation for MCP tool parameters

## MCP Tool Usage (For AI Models)

### Essential Workflow
**ALWAYS follow this pattern when working with code:**

1. **Before making ANY changes**: `start_vibing()`
2. **Make your code changes** (files are auto-committed every second)
3. **When finished**: `stop_vibing(commit_message="Your feature description")`

### Available Tools

#### `start_vibing()`
- **When to use**: FIRST thing before editing any files
- **What it does**: Creates git branch from latest main, starts auto-commit watcher
- **Safe to call**: Multiple times (idempotent)
- **Handles uncommitted changes**: Prompts to use one of the helper functions below

#### `stop_vibing(commit_message)`
- **When to use**: ONLY when user explicitly asks to stop or says they're done
- **What it does**: Squashes commits, rebases on main, creates PR
- **Safe to call**: Even if not vibing (idempotent)
- **IMPORTANT**: Do NOT call automatically - wait for user confirmation
- **Commit message format**: First line becomes PR title, full message becomes PR body
- **Example**: 
  ```
  stop_vibing(commit_message="""Add user authentication system
  
  - Implemented JWT-based authentication
  - Added login/logout endpoints
  - Created middleware for protected routes
  - Updated user model with password hashing""")
  ```

#### `vibe_status()`
- **When to use**: Check current session state
- **Returns**: 🟢 VIBING | 🔵 IDLE | ⚪ NOT INITIALIZED

#### `stash_and_vibe()`
- **When to use**: Have uncommitted changes but want to start fresh from main
- **What it does**: Stashes changes, switches to main, starts vibing
- **Restore changes**: Use `git stash pop` after vibing

#### `commit_and_vibe()`
- **When to use**: Want to save current work before starting fresh
- **What it does**: Commits as "WIP", switches to main, starts vibing

#### `vibe_from_here()`
- **When to use**: Want to start vibing with current changes
- **What it does**: Starts vibing from current branch/state
- **Auto-commits**: Any existing uncommitted changes

### Example Sessions

#### Starting fresh from main:
```
1. vibe_status() → "🔵 IDLE: Ready to start vibing"
2. start_vibing() → "🚀 Started vibing! Auto-committing changes"
3. [Make code changes - all auto-committed]
4. stop_vibing(commit_message="Implement login feature") → "🏁 PR created!"
```

#### With uncommitted changes:
```
1. start_vibing() → "⚠️ Uncommitted changes detected!"
2. stash_and_vibe() → "🚀 Started vibing! Your changes are stashed."
3. [Make code changes]
4. stop_vibing(commit_message="New feature") → "🏁 PR created!"
5. git stash pop → Restore your original changes
```


### Error Recovery
- All tools are **idempotent** - safe to call multiple times
- If unsure of state, call `vibe_status()` first
- Tools provide clear feedback about current state

## Development Guidelines

### When implementing new features:
1. Use `@beartype` decorators for runtime type checking
2. Model states as frozen dataclasses
3. Use `@dispatch` for handling different states/types
4. Create semantic types with `NewType` for domain concepts
5. Use `Annotated` types with validators for constraints

### Example Patterns:

#### Type-Safe Functions:
```python
@beartype
def find_git_repo() -> GitPath:
    """Returns a Path that's guaranteed to be a git repo"""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".git").exists():
            return GitPath(current)
        current = current.parent
    raise RuntimeError("Not in a git repository")
```

#### Multiple Dispatch:
```python
@dispatch
def run_command(args: list[str], cwd: Path | None = None) -> CommandResult:
    """List version"""

@dispatch  
def run_command(command: str, cwd: Path | None = None) -> CommandResult:
    """String version - auto-splits"""
    return run_command(command.split(), cwd)
```

#### State Transitions:
```python
@contextmanager
def atomic_state_transition(session: VibeSession):
    """Ensure state transitions are atomic"""
    original_state = session.state
    try:
        yield
    except Exception:
        session.state = original_state
        raise
```

## Testing Strategy
- Unit tests for type validation
- Integration tests for full workflows
- Mutation testing with mutmut for 100% coverage
- Type safety tests to verify beartype catches errors