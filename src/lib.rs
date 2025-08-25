use std::marker::PhantomData;

/// Marker type for the session before it has started.
pub struct Idle;

/// Marker type for an active vibing session.
pub struct Vibing;

/// Marker type for a completed session.
pub struct Finished;

/// A session that transitions through compile-time states.
pub struct VibeSession<State> {
    branch: String,
    state: PhantomData<State>,
}

impl VibeSession<Idle> {
    /// Create a new session in the idle state.
    pub fn new(branch: impl Into<String>) -> Self {
        Self {
            branch: branch.into(),
            state: PhantomData,
        }
    }

    /// Start vibing, transitioning to the `Vibing` state.
    pub fn start(self) -> VibeSession<Vibing> {
        VibeSession {
            branch: self.branch,
            state: PhantomData,
        }
    }
}

impl VibeSession<Vibing> {
    /// Finish vibing, transitioning to the `Finished` state.
    pub fn finish(self) -> VibeSession<Finished> {
        VibeSession {
            branch: self.branch,
            state: PhantomData,
        }
    }

    /// Access the active branch name.
    pub fn branch(&self) -> &str {
        &self.branch
    }
}

impl VibeSession<Finished> {
    /// Access the branch name after completion.
    pub fn branch(&self) -> &str {
        &self.branch
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn typestate_transitions() {
        let idle = VibeSession::<Idle>::new("feature-branch");
        let vibing = idle.start();
        assert_eq!(vibing.branch(), "feature-branch");
        let finished = vibing.finish();
        assert_eq!(finished.branch(), "feature-branch");
    }
}

