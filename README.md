# vibe-git (Rust)

vibe-git demonstrates typestate programming for managing git workflows. It
exposes a high-level `McpClient` that drives a `VibeSession` through `Idle`,
`Vibing`, and `Finished` states while switching branches with real git
commands.

## Installation

Clone the repository and install the crate locally:

```
git clone <repo>
cd vibe-git
cargo install --path .
```

You can also use the crate directly in another project by adding it to your
`Cargo.toml`.

## Usage

Example driving a session via the `McpClient` facade:

```
use vibe_git::McpClient;

let mut client = McpClient::new();
client.start_vibing("feature-branch");
// make code changes on the new branch
client.stop_vibing();
```

Run the bundled MCP client binary:

```
cargo run --bin vibe-git-mcp
```

## Development

```
cargo test
```
