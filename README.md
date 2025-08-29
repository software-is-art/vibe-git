# vibe-git (Rust)

vibe-git demonstrates typestate programming for managing git workflows. It
exposes a high-level `McpClient` that drives a `VibeSession` through `Idle`,
`Vibing`, and `Finished` states while switching branches with real git
commands.

## Installation

Install from crates.io:

```
cargo install vibe-git
```

If the crate isn't available on crates.io yet or you want the latest code, you
can install directly from git:

```
cargo install --git <repo> vibe-git
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
Ensure you have a recent Rust toolchain installed. Common development tasks:

```bash
# format code
cargo fmt --all -- --check

# lint
cargo clippy --all-targets --all-features -- -D warnings

# run tests
cargo test
```

### Release

Publishing to crates.io is automated via GitHub Actions. Pushing a tag like
`v0.1.0` will trigger the workflow to run `cargo publish` using the
`CARGO_REGISTRY_TOKEN` secret.
