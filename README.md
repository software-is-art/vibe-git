# vibe-git

[![Tests](https://github.com/software-is-art/vibe-git/actions/workflows/test.yml/badge.svg)](https://github.com/software-is-art/vibe-git/actions/workflows/test.yml)
[![Mutation Score](https://img.shields.io/badge/mutation%20score-100%25-brightgreen.svg)](https://github.com/boxed/mutmut)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-compatible-purple.svg)](https://github.com/modelcontextprotocol)

**Never lose work again when AI coding goes wrong.**

## 🛡️ The Problem

You're working with AI to build something amazing. The AI is making changes, experimenting, trying different approaches. Then something goes wrong - a bad edit, a mistaken deletion, or the AI gets confused and breaks everything. 

**Your work is gone.** 

Whether you're a seasoned developer or completely new to coding, this is infuriating. You can't relax and let the AI explore freely because you're constantly worried about losing progress.

## ✨ The Solution

vibe-git automatically commits every single change as you work, so you can **completely relax** and let AI coding flow:

- **🔄 Every change is instantly saved** - No more "oh no, I lost 30 minutes of work"
- **🌊 Let the AI experiment freely** - Try wild ideas without fear
- **⏪ Easy to undo anything** - Every step is preserved in git history
- **🎯 Clean final result** - All those messy auto-commits become one clean, professional commit that represents your final logical change
- **🚀 Automatic pull requests** - Share your work with zero git commands

**For Git beginners**: You don't need to know anything about git. Just code.  
**For Git experts**: You get all the safety of continuous commits with none of the manual work.

## 🌟 How It Works

1. **Start vibing**: "Hey Claude, start a vibe session"
   - Creates a safe branch for your experiments
   - Every file change gets automatically committed

2. **Code without fear**: Make any changes you want
   - Try different approaches, let the AI experiment
   - Everything is safely preserved, always

3. **Finish clean**: "I'm done, let's create a PR"
   - All the messy "auto-commit" messages disappear
   - You get one clean commit with a proper description of what changed
   - Automatically creates a professional pull request ready for review

## 🎯 Perfect For

- **AI-assisted development** - Never lose work when the AI makes mistakes
- **Rapid prototyping** - Experiment freely without git ceremony  
- **Learning to code** - Focus on coding, not git commands
- **Pair programming with AI** - Let your AI partner be bold and creative
- **Exploratory coding** - Try ideas without commitment anxiety

## 📦 Installation

### Prerequisites

- Python 3.13+ 
- [uv](https://docs.astral.sh/uv/) package manager
- Git repository with a `main` or `master` branch
- GitHub CLI (`gh`) for automatic PR creation (optional)

### Option 1: Direct from Git (Recommended)

Add to your Claude Code `.mcp.json` configuration:

```json
{
  "mcpServers": {
    "vibe-git": {
      "command": "uvx",
      "args": [
        "--from", 
        "git+https://github.com/software-is-art/vibe-git.git",
        "vibe-git-mcp"
      ],
      "cwd": "/path/to/your/git/repository"
    }
  }
}
```

**Important**: Replace `/path/to/your/git/repository` with the absolute path to your git repository.

### Option 2: Local Development

1. Clone the repository:
```bash
git clone https://github.com/software-is-art/vibe-git.git
cd vibe-git
```

2. Install dependencies:
```bash
uv sync
```

3. Add to your `.mcp.json`:
```json
{
  "mcpServers": {
    "vibe-git": {
      "command": "uv",
      "args": ["run", "python", "main.py"],
      "cwd": "/absolute/path/to/vibe-git"
    }
  }
}
```

## 🔧 Usage

Once installed, vibe-git provides three MCP tools:

### `start_vibing()`
🚀 **Call this FIRST** before making any code changes!
- Creates a new git branch (or reuses existing vibe branch)
- Starts real-time file watching
- Auto-commits every file change instantly

### `vibe_status()`
📊 Check the current vibe session status
- Shows if you're currently vibing or idle
- Displays the active branch name

### `stop_vibing(commit_message)`
🏁 **Call this when you're done** with your changes
- Squashes all auto-commits into a single meaningful commit
- Rebases on latest main branch
- Pushes to remote and creates a pull request
- **Only call when user explicitly asks to stop!**

## 💫 Real-World Example

**Before vibe-git**: "Claude, can you help me add user authentication?"
- *30 minutes later* "Oh no, the AI broke something and I lost all my work!"
- *Start over, cautiously*

**With vibe-git**: "Claude, start a vibe session and let's add user authentication!"
- AI experiments freely with different approaches
- You see the history of every change in git
- AI makes a mistake? No problem - every step is saved
- "Let's try that completely differently!" - Go wild!
- "I'm done, create a PR" - Professional result, zero stress

## 🚀 Simple Workflow

1. **"Start vibing"** 
   - Your AI creates a safe experimental branch
   - Every keystroke is automatically saved

2. **Code fearlessly**
   - Try different ideas, let the AI experiment
   - Make mistakes - they're all recoverable
   - Focus on the problem, not the process

3. **"Let's finish this up"**
   - All those messy auto-saves become one clean commit
   - Professional pull request created automatically
   - Ready to share your work

## ⚙️ How it Works

### Event-Driven File Watching
- Uses Python's `watchdog` library for real-time file system monitoring
- Commits happen instantly when files change (no polling delays)
- Smart filtering ignores `.git`, `__pycache__`, `.venv`, and other temp files
- Rate limiting prevents spam from rapid file changes

### Intelligent Git Operations
- Automatically handles branch creation and switching
- Squashes messy auto-commits into clean, meaningful commits
- Rebases on latest main to avoid merge conflicts
- Creates PRs with descriptive titles and bodies

### MCP Integration
- Built with FastMCP for reliable protocol compliance
- Proper error handling and status reporting
- Works seamlessly with Claude Code

## 🛡️ Safety Features

- **Idempotent operations**: Safe to call tools multiple times
- **Graceful cleanup**: File watchers stop properly on session end
- **Error recovery**: Handles git conflicts and network issues
- **State consistency**: Detects and recovers from inconsistent states

## ⚙️ Configuration

The server automatically:
- Detects your git repository root
- Finds the main/master branch
- Respects standard gitignore patterns
- Uses timestamps for unique branch names

No additional configuration needed!

## 🔧 Troubleshooting

### "Not in a git repository"
Make sure the `cwd` in your `.mcp.json` points to a directory inside a git repository.

### "Could not checkout main/master branch"
Ensure your repository has a `main` or `master` branch that you can switch to.

### Auto-commits not working
Check that:
- You called `start_vibing()` first
- You're editing files that aren't in `.gitignore`
- The MCP server is still running (check Claude Code connection status)

### PR creation fails
Ensure GitHub CLI (`gh`) is installed and authenticated:
```bash
gh auth login
```

## 🧪 Testing

We take code quality seriously! This project features:

- **100% mutation testing score** - All mutants killed using [mutmut](https://github.com/boxed/mutmut)
- **Comprehensive integration tests** - Testing all MCP tools and edge cases
- **CI/CD with GitHub Actions** - Automated testing on every PR
- **Runtime type safety** - Using [beartype](https://github.com/beartype/beartype) for validation

To run tests locally:
```bash
# Run all tests
uv run pytest

# Run mutation testing
uv run mutmut run
```

## 🏗️ Architecture

This project uses modern Python patterns for reliability and maintainability:

- **[beartype](https://github.com/beartype/beartype)** - Runtime type checking for safer code
- **[plum-dispatch](https://github.com/beartype/plum)** - Multiple dispatch for clean code organization
- **Type-safe state machine** - Explicit states prevent invalid operations
- **Semantic types** - `GitPath`, `BranchName`, etc. for self-documenting code

## 🤝 Contributing

Contributions welcome! This is a Python project using:
- **FastMCP** for MCP server implementation
- **watchdog** for file system monitoring  
- **beartype** for runtime type validation
- **plum** for multiple dispatch patterns
- **uv** for dependency management
- **pytest** for testing
- **mutmut** for mutation testing

## 📄 License

MIT License - see LICENSE file for details.

---

**Happy vibe coding! 🎉**
