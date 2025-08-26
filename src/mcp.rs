use crate::{Idle, VibeSession, Vibing};

/// Simple client API for driving a vibe session.
pub struct McpClient {
    session: Option<VibeSession<Vibing>>,
}

impl McpClient {
    /// Create a new client with no active session.
    pub fn new() -> Self {
        Self { session: None }
    }

    /// Start vibing on the given branch if not already active.
    pub fn start_vibing(&mut self, branch: impl AsRef<str>) {
        if self.session.is_none() {
            let idle = VibeSession::<Idle>::new(branch.as_ref());
            self.session = Some(idle.start());
        }
    }

    /// Stop the current vibing session if one is active.
    pub fn stop_vibing(&mut self) {
        if let Some(vibing) = self.session.take() {
            let _finished = vibing.finish();
        }
    }

    /// Return the active branch name, if any.
    pub fn branch(&self) -> Option<&str> {
        self.session.as_ref().map(|s| s.branch())
    }
}

impl Default for McpClient {
    fn default() -> Self {
        Self::new()
    }
}
