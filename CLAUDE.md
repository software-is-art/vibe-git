# vibe-git MCP Server

## Project Overview
An MCP (Model Context Protocol) server that enables friction-free git workflows for "vibe coding" - allowing developers to focus on code while git operations happen automatically in the background.

## Core Functionality
- `start_vibing`: Creates a new branch and auto-commits all changes every second
- `stop_vibing`: Squashes commits, rebases on main, and creates a PR

## Architecture Decisions

### Language: Rust
We're using Rust for performance, memory safety, and its excellent type system.

### Typestate Programming Pattern
This project extensively uses the typestate pattern to encode state transitions at the type level, preventing invalid operations at compile time.

#### Example States:
```rust
// Vibe session states
struct Idle;
struct Vibing { branch: String, watcher: FileWatcher };
struct Stopping { branch: String };

// Git repository states  
struct Clean;
struct Dirty;
struct Detached;
```

#### Key Benefits:
1. **Compile-time guarantees**: Can't call `stop_vibing` when not vibing
2. **Self-documenting**: Types express valid operations
3. **Zero runtime cost**: All checks happen at compile time
4. **Prevents race conditions**: State transitions are explicit

### Dependencies
- `rmcp`: Official MCP Rust SDK for protocol implementation
- `rmcp-macros`: Procedural macros for MCP tool declarations
- `git2`: Native git operations
- `notify`: Cross-platform file watching
- `tokio`: Async runtime

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
1. Model states as zero-sized types
2. Use phantom types to track state
3. Implement state transitions as consuming methods
4. Never use runtime state checks when compile-time checks are possible

### Example Pattern:
```rust
impl VibeSession<Idle> {
    fn start_vibing(self) -> Result<VibeSession<Vibing>, Error> {
        // Transition from Idle to Vibing
    }
}

impl VibeSession<Vibing> {
    fn stop_vibing(self, message: String) -> Result<VibeSession<Idle>, Error> {
        // Can only stop when vibing
    }
}
```

## Testing Strategy
- Unit tests for each state transition
- Integration tests for full workflows
- Property-based tests for state machine invariants