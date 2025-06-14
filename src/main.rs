use anyhow::{Result, anyhow};
use rmcp::ServiceExt;
use std::env;
use std::path::PathBuf;
use vibe_git::service::VibeGitService;

fn find_git_repository() -> Result<PathBuf> {
    let mut current_dir = env::current_dir()?;
    
    loop {
        if current_dir.join(".git").exists() {
            return Ok(current_dir);
        }
        
        match current_dir.parent() {
            Some(parent) => current_dir = parent.to_path_buf(),
            None => return Err(anyhow!("No git repository found in current directory or any parent directory")),
        }
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    // Get repo path from args or discover git repository
    let repo_path = env::args()
        .nth(1)
        .map(PathBuf::from)
        .unwrap_or_else(|| find_git_repository().expect("Failed to find git repository"));
    
    // Create the vibe-git service
    let service = VibeGitService::new(repo_path)?;
    
    // Create stdio transport (using stdin/stdout)
    let transport = (tokio::io::stdin(), tokio::io::stdout());
    
    // Start the MCP server
    let server = service.serve(transport).await?;
    
    // Wait for the server to complete
    let _quit_reason = server.waiting().await?;
    
    Ok(())
}