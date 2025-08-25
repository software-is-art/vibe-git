# vibe-git (Rust)

This repository has been rewritten in Rust. It demonstrates typestate programming
for managing domain state transitions at compile time.

The core library exposes a `VibeSession` type that moves through `Idle`,
`Vibing`, and `Finished` states using the type system to prevent invalid
transitions.

## Development

```
cargo test
```
