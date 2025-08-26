use std::process::Command;
use tempfile::tempdir;
use vibe_git::McpClient;

#[test]
fn mcp_client_switches_branches() {
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

    let mut client = McpClient::new();
    client.start_vibing("integration-branch");

    let branch = String::from_utf8(
        Command::new("git")
            .args(["rev-parse", "--abbrev-ref", "HEAD"])
            .output()
            .unwrap()
            .stdout,
    )
    .unwrap();
    assert_eq!(branch.trim(), "integration-branch");

    client.stop_vibing();
    let branch = String::from_utf8(
        Command::new("git")
            .args(["rev-parse", "--abbrev-ref", "HEAD"])
            .output()
            .unwrap()
            .stdout,
    )
    .unwrap();
    assert_eq!(branch.trim(), "main");
}
