use std::{fmt, marker::PhantomData, process::Command};

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct BranchName(String);

impl BranchName {
    pub fn as_str(&self) -> &str {
        &self.0
    }
}

impl From<&str> for BranchName {
    fn from(value: &str) -> Self {
        Self(value.to_string())
    }
}

impl From<String> for BranchName {
    fn from(value: String) -> Self {
        Self(value)
    }
}

impl AsRef<str> for BranchName {
    fn as_ref(&self) -> &str {
        &self.0
    }
}

impl fmt::Display for BranchName {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        self.0.fmt(f)
    }
}

mod mcp;

pub use mcp::McpClient;

/// Marker type for the session before it has started.
pub struct Idle;

/// Marker type for an active vibing session.
pub struct Vibing;

/// Marker type for a completed session.
pub struct Finished;

/// A session that transitions through compile-time states.
pub struct VibeSession<State> {
    branch: BranchName,
    state: PhantomData<State>,
}

impl VibeSession<Idle> {
    /// Create a new session in the idle state.
    pub fn new(branch: impl Into<BranchName>) -> Self {
        Self {
            branch: branch.into(),
            state: PhantomData,
        }
    }

    /// Start vibing, transitioning to the `Vibing` state.
    pub fn start(self) -> VibeSession<Vibing> {
        let status = Command::new("git")
            .args(["checkout", "-b", self.branch.as_ref()])
            .status()
            .expect("failed to run git checkout");
        assert!(status.success(), "git checkout failed");

        VibeSession {
            branch: self.branch,
            state: PhantomData,
        }
    }
}

impl VibeSession<Vibing> {
    /// Finish vibing, transitioning to the `Finished` state.
    pub fn finish(self) -> VibeSession<Finished> {
        let status = Command::new("git")
            .args(["checkout", "main"])
            .status()
            .expect("failed to checkout main");
        assert!(status.success(), "git checkout main failed");

        VibeSession {
            branch: self.branch,
            state: PhantomData,
        }
    }

    /// Access the active branch name.
    pub fn branch(&self) -> &BranchName {
        &self.branch
    }
}

impl VibeSession<Finished> {
    /// Access the branch name after completion.
    pub fn branch(&self) -> &BranchName {
        &self.branch
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::process::Command;
    use tempfile::tempdir;

    #[test]
    fn typestate_transitions() {
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

        let idle = VibeSession::<Idle>::new("feature-branch");
        let vibing = idle.start();
        assert_eq!(vibing.branch().as_ref(), "feature-branch");
        let finished = vibing.finish();
        assert_eq!(finished.branch().as_ref(), "feature-branch");
    }
}
