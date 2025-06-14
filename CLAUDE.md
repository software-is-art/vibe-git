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
- **What it does**: Creates git branch, starts auto-commit watcher
- **Safe to call**: Multiple times (idempotent)
- **Example**: Always call this before implementing features

#### `stop_vibing(commit_message)`
- **When to use**: After completing your changes  
- **What it does**: Squashes commits, rebases on main, creates PR
- **Safe to call**: Even if not vibing (idempotent)
- **Example**: `stop_vibing(commit_message="Add user authentication system")`

#### `vibe_status()`
- **When to use**: Check current session state
- **Returns**: 🟢 VIBING | 🔵 IDLE | ⚪ NOT INITIALIZED

### Example Session
```
1. vibe_status() → "🔵 IDLE: Ready to start vibing"
2. start_vibing() → "🚀 Started vibing! Auto-committing changes"
3. [Make code changes - all auto-committed]
4. stop_vibing(commit_message="Implement login feature") → "🏁 PR created!"
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