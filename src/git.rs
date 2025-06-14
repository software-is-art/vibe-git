use anyhow::{Result, Context};
use git2::{Repository, BranchType, ResetType};
use std::path::Path;

pub fn validate_repository(path: &Path) -> Result<()> {
    Repository::open(path)
        .context("Not a valid git repository")?;
    Ok(())
}

pub fn create_branch_from_main(repo_path: &Path, branch_name: &str) -> Result<()> {
    let repo = Repository::open(repo_path)?;
    
    // Get main branch
    let main_branch = repo.find_branch("main", BranchType::Local)
        .or_else(|_| repo.find_branch("master", BranchType::Local))
        .context("Could not find main/master branch")?;
    
    let main_commit = main_branch.get().peel_to_commit()?;
    
    // Create new branch from main
    repo.branch(branch_name, &main_commit, false)?;
    
    Ok(())
}

pub fn checkout_branch(repo_path: &Path, branch_name: &str) -> Result<()> {
    let repo = Repository::open(repo_path)?;
    let obj = repo.revparse_single(&format!("refs/heads/{}", branch_name))?;
    
    repo.checkout_tree(&obj, None)?;
    repo.set_head(&format!("refs/heads/{}", branch_name))?;
    
    Ok(())
}

pub fn create_branch(repo_path: &Path, branch_name: &str) -> Result<()> {
    let repo = Repository::open(repo_path)?;
    let head = repo.head()?.peel_to_commit()?;
    
    repo.branch(branch_name, &head, false)?;
    
    Ok(())
}

pub fn pull(repo_path: &Path) -> Result<()> {
    // For now, using simple fetch + merge
    // In production, would use proper fetch/merge with conflict handling
    let repo = Repository::open(repo_path)?;
    
    // Check if origin remote exists (skip pull in local-only repos like tests)
    if repo.find_remote("origin").is_err() {
        return Ok(()); // No remote, skip pull
    }
    
    let mut remote = repo.find_remote("origin")?;
    remote.fetch(&["main"], None, None)?;
    
    // Fast-forward merge
    let fetch_head = repo.find_reference("FETCH_HEAD")?;
    let fetch_commit = fetch_head.peel_to_commit()?;
    let annotated_commit = repo.find_annotated_commit(fetch_commit.id())?;
    let analysis = repo.merge_analysis(&[&annotated_commit])?;
    
    if analysis.0.is_fast_forward() {
        let mut reference = repo.find_reference("HEAD")?;
        reference.set_target(fetch_commit.id(), "Fast-forward")?;
        repo.reset(&fetch_commit.into_object(), ResetType::Hard, None)?;
    }
    
    Ok(())
}

pub fn squash_rebase_onto_main(repo_path: &Path, message: &str) -> Result<()> {
    let repo = Repository::open(repo_path)?;
    
    // Get current branch commits since divergence from main
    let main_oid = repo.revparse_single("main")?.id();
    let _head_oid = repo.head()?.target().unwrap();
    
    // Reset to main
    let main_obj = repo.find_object(main_oid, None)?;
    repo.reset(&main_obj, ResetType::Soft, None)?;
    
    // Create single commit with all changes
    let sig = repo.signature()?;
    let tree_id = repo.index()?.write_tree()?;
    let tree = repo.find_tree(tree_id)?;
    let parent = repo.find_commit(main_oid)?;
    
    repo.commit(
        Some("HEAD"),
        &sig,
        &sig,
        message,
        &tree,
        &[&parent],
    )?;
    
    Ok(())
}

pub fn push_branch(repo_path: &Path, branch_name: &str) -> Result<()> {
    // Check if we have a remote (skip push in local-only repos like tests)
    let repo = Repository::open(repo_path)?;
    if repo.find_remote("origin").is_err() {
        return Ok(()); // No remote, skip push
    }
    
    // This is a simplified version - in production would handle auth
    std::process::Command::new("git")
        .current_dir(repo_path)
        .args(&["push", "-u", "origin", branch_name, "--force"])
        .output()
        .context("Failed to push branch")?;
    
    Ok(())
}

pub fn create_pr(repo_path: &Path, branch_name: &str, message: &str) -> Result<()> {
    // Check if we have a remote (skip PR creation in local-only repos like tests)
    let repo = Repository::open(repo_path)?;
    if repo.find_remote("origin").is_err() {
        return Ok(()); // No remote, skip PR creation
    }
    
    // Using GitHub CLI for simplicity
    std::process::Command::new("gh")
        .current_dir(repo_path)
        .args(&["pr", "create", "--title", message, "--body", message, "--head", branch_name])
        .output()
        .context("Failed to create PR (is gh CLI installed?)")?;
    
    Ok(())
}