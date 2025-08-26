use std::process::Command;
use tempfile::tempdir;
use vibe_git::{Idle, VibeSession};

#[test]

/// Verify MCP-style typestate flow across git branches.


fn typestate_flow_with_git() {
    let dir = tempdir().unwrap();
    std::env::set_current_dir(&dir).unwrap();


    Command::new("git")
        .args(["init", "-b", "main"])
        .status()
        .unwrap();

    Command::new("git")
        .args(["config", "user.email", "test@example.com"])
        .status()
        .unwrap();
    Command::new("git")
        .args(["config", "user.name", "Test User"])
        .status()
        .unwrap();
    Command::new("git")
        .args(["commit", "--allow-empty", "-m", "init"])
        .status()
        .unwrap();

    let idle = VibeSession::<Idle>::new("integration-branch");
    let vibing = idle.start();

    let branch = String::from_utf8(
        Command::new("git")
            .args(["rev-parse", "--abbrev-ref", "HEAD"])
            .output()
            .unwrap()
            .stdout,
    )
    .unwrap();
    assert_eq!(branch.trim(), "integration-branch");
    assert_eq!(vibing.branch(), "integration-branch");

    let finished = vibing.finish();
    let branch = String::from_utf8(
        Command::new("git")
            .args(["rev-parse", "--abbrev-ref", "HEAD"])
            .output()
            .unwrap()
            .stdout,
    )
    .unwrap();
    assert_eq!(branch.trim(), "main");
    assert_eq!(finished.branch(), "integration-branch");
}
