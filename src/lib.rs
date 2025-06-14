pub mod typestate;
pub mod git;
pub mod watcher;
pub mod service;

use std::marker::PhantomData;
use std::path::PathBuf;
use anyhow::Result;

/// Type-safe vibe session using typestate pattern
#[derive(Debug)]
pub struct VibeSession<State> {
    repo_path: PathBuf,
    state: PhantomData<State>,
}

/// Session states
#[derive(Debug)]
pub struct Idle;

#[derive(Debug)]
pub struct Vibing;

impl VibeSession<Idle> {
    pub fn new(repo_path: PathBuf) -> Result<Self> {
        // Validate repo exists
        git::validate_repository(&repo_path)?;
        
        Ok(VibeSession {
            repo_path,
            state: PhantomData,
        })
    }
    
    pub fn start_vibing(self) -> Result<(VibeSession<Vibing>, String)> {
        let branch_name = format!("vibe-{}", chrono::Utc::now().timestamp());
        
        // Create branch from main
        git::create_branch_from_main(&self.repo_path, &branch_name)?;
        git::checkout_branch(&self.repo_path, &branch_name)?;
        
        // Start file watcher
        let _watcher_handle = watcher::start_auto_commit(self.repo_path.clone())?;
        
        Ok((
            VibeSession {
                repo_path: self.repo_path,
                state: PhantomData,
            },
            branch_name,
        ))
    }
}

impl VibeSession<Vibing> {
    pub fn stop_vibing(self, branch_name: String, commit_message: String) -> Result<VibeSession<Idle>> {
        
        // Stop watcher (would be stored in state)
        // watcher_handle.stop()?;
        
        // Create backup branch
        let backup_name = format!("backup-{}", branch_name);
        git::create_branch(&self.repo_path, &backup_name)?;
        
        // Pull latest main
        git::checkout_branch(&self.repo_path, "main")?;
        git::pull(&self.repo_path)?;
        
        // Checkout vibe branch and squash
        git::checkout_branch(&self.repo_path, &branch_name)?;
        git::squash_rebase_onto_main(&self.repo_path, &commit_message)?;
        
        // Push and create PR
        git::push_branch(&self.repo_path, &branch_name)?;
        git::create_pr(&self.repo_path, &branch_name, &commit_message)?;
        
        // Return to main branch for clean state
        git::checkout_branch(&self.repo_path, "main")?;
        
        Ok(VibeSession {
            repo_path: self.repo_path,
            state: PhantomData,
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::TempDir;
    use std::process::Command;

    fn setup_test_repo() -> Result<TempDir> {
        let temp_dir = TempDir::new()?;
        let repo_path = temp_dir.path();
        
        // Initialize git repo
        Command::new("git")
            .current_dir(repo_path)
            .args(&["init"])
            .output()?;
            
        // Set up git config for tests
        Command::new("git")
            .current_dir(repo_path)
            .args(&["config", "user.name", "Test User"])
            .output()?;
            
        Command::new("git")
            .current_dir(repo_path)
            .args(&["config", "user.email", "test@example.com"])
            .output()?;
            
        // Create initial commit on main
        std::fs::write(repo_path.join("README.md"), "# Test Repository")?;
        Command::new("git")
            .current_dir(repo_path)
            .args(&["add", "README.md"])
            .output()?;
            
        Command::new("git")
            .current_dir(repo_path)
            .args(&["commit", "-m", "Initial commit"])
            .output()?;
            
        Ok(temp_dir)
    }

    #[test]
    fn test_vibe_session_creation() -> Result<()> {
        let temp_dir = setup_test_repo()?;
        let repo_path = temp_dir.path().to_path_buf();
        
        let session = VibeSession::new(repo_path)?;
        
        // Type check - this is a compile-time guarantee, runtime check is just for demonstration
        let _: VibeSession<Idle> = session;
        
        Ok(())
    }

    #[tokio::test]
    async fn test_typestate_transition_idle_to_vibing() -> Result<()> {
        let temp_dir = setup_test_repo()?;
        let repo_path = temp_dir.path().to_path_buf();
        
        let idle_session = VibeSession::new(repo_path)?;
        
        // Start vibing - this consumes the idle session
        let (vibing_session, branch_name) = idle_session.start_vibing()?;
        
        // Verify branch was created
        assert!(branch_name.starts_with("vibe-"));
        
        // Type check - this is a compile-time guarantee
        let _: VibeSession<Vibing> = vibing_session;
        
        Ok(())
    }

    #[tokio::test]
    async fn test_typestate_transition_vibing_to_idle() -> Result<()> {
        let temp_dir = setup_test_repo()?;
        let repo_path = temp_dir.path().to_path_buf();
        
        let idle_session = VibeSession::new(repo_path)?;
        let (vibing_session, branch_name) = idle_session.start_vibing()?;
        
        // Stop vibing - this consumes the vibing session
        let idle_session = vibing_session.stop_vibing(branch_name, "Test commit".to_string())?;
        
        // Type check - this is a compile-time guarantee
        let _: VibeSession<Idle> = idle_session;
        
        Ok(())
    }

    #[tokio::test]
    async fn test_full_vibe_workflow() -> Result<()> {
        let temp_dir = setup_test_repo()?;
        let repo_path = temp_dir.path().to_path_buf();
        
        // 1. Create idle session
        let session = VibeSession::new(repo_path.clone())?;
        
        // 2. Start vibing
        let (vibing_session, branch_name) = session.start_vibing()?;
        
        // 3. Make some changes (simulate file modifications)
        std::fs::write(repo_path.join("test_file.txt"), "Hello vibe-git!")?;
        
        // 4. Stop vibing
        let _idle_session = vibing_session.stop_vibing(branch_name.clone(), "Add test file".to_string())?;
        
        // 5. Verify we're back on main branch
        let output = Command::new("git")
            .current_dir(&repo_path)
            .args(&["branch", "--show-current"])
            .output()?;
            
        let output_str = String::from_utf8_lossy(&output.stdout);
        let current_branch = output_str.trim();
        assert_eq!(current_branch, "main");
        
        Ok(())
    }
}