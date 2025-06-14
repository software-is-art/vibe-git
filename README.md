# vibe-git

Friction-free git workflows for vibe coding - focus on code while git operations happen automatically in the background.

## =€ What is vibe-git?

vibe-git is an MCP (Model Context Protocol) server that enables "vibe coding" - a workflow where you can focus entirely on writing code while git operations happen automatically:

- **Auto-commits**: Every file change is instantly committed to a dedicated branch
- **Smart cleanup**: When done, all commits are squashed into a meaningful commit message
- **Seamless PRs**: Automatically rebases on main and creates a pull request
- **Zero friction**: No manual git commands needed during development

Perfect for exploratory coding, prototyping, or any time you want to focus on the code instead of git ceremony.

## =æ Installation

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

## <¯ Usage

Once installed, vibe-git provides three MCP tools:

### `start_vibing()`
=€ **Call this FIRST** before making any code changes!
- Creates a new git branch (or reuses existing vibe branch)
- Starts real-time file watching
- Auto-commits every file change instantly

### `vibe_status()`
=Ê Check the current vibe session status
- Shows if you're currently vibing or idle
- Displays the active branch name

### `stop_vibing(commit_message)`
<Á **Call this when you're done** with your changes
- Squashes all auto-commits into a single meaningful commit
- Rebases on latest main branch
- Pushes to remote and creates a pull request
- **Only call when user explicitly asks to stop!**

## = Typical Workflow

1. **Start vibing**: "Hey Claude, start a vibe session"
   - Claude calls `start_vibing()`
   - You're now on a vibe branch with auto-commits enabled

2. **Code freely**: Make any changes you want
   - Every file save triggers an instant auto-commit
   - No need to think about git at all

3. **Finish up**: "I'm done, let's wrap this up"
   - Claude calls `stop_vibing("Implement new feature X")`
   - All commits are squashed, rebased, and PR'd automatically

## ™ How it Works

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

## =á Safety Features

- **Idempotent operations**: Safe to call tools multiple times
- **Graceful cleanup**: File watchers stop properly on session end
- **Error recovery**: Handles git conflicts and network issues
- **State consistency**: Detects and recovers from inconsistent states

## =' Configuration

The server automatically:
- Detects your git repository root
- Finds the main/master branch
- Respects standard gitignore patterns
- Uses timestamps for unique branch names

No additional configuration needed!

## = Troubleshooting

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

## > Contributing

Contributions welcome! This is a Python project using:
- **FastMCP** for MCP server implementation
- **watchdog** for file system monitoring  
- **uv** for dependency management

## =Ä License

MIT License - see LICENSE file for details.

---

**Happy vibe coding! =€**