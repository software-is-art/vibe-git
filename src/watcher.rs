use anyhow::Result;
use notify::{Config, Event, RecommendedWatcher, RecursiveMode, Watcher};
use std::path::PathBuf;
use std::sync::mpsc::{channel, Sender};
use std::time::Duration;
use tokio::task::JoinHandle;

pub struct WatcherHandle {
    shutdown_tx: Sender<()>,
    task_handle: JoinHandle<()>,
}

impl WatcherHandle {
    pub fn stop(self) -> Result<()> {
        self.shutdown_tx.send(())?;
        // In production, would properly await the handle
        Ok(())
    }
}

pub fn start_auto_commit(repo_path: PathBuf) -> Result<WatcherHandle> {
    let (shutdown_tx, shutdown_rx) = channel();
    let (event_tx, event_rx) = channel();
    
    // Create watcher
    let mut watcher = RecommendedWatcher::new(
        move |res: Result<Event, notify::Error>| {
            if let Ok(event) = res {
                let _ = event_tx.send(event);
            }
        },
        Config::default().with_poll_interval(Duration::from_secs(1)),
    )?;
    
    // Watch repository, excluding .git directory
    watcher.watch(&repo_path, RecursiveMode::Recursive)?;
    
    // Spawn commit task
    let task_handle = tokio::spawn(async move {
        let mut last_commit = std::time::Instant::now();
        
        loop {
            // Check for shutdown
            if shutdown_rx.try_recv().is_ok() {
                break;
            }
            
            // Process events
            while let Ok(event) = event_rx.try_recv() {
                // Skip .git directory events
                if event.paths.iter().any(|p| p.to_string_lossy().contains(".git")) {
                    continue;
                }
                
                // Commit if 1 second has passed
                if last_commit.elapsed() >= Duration::from_secs(1) {
                    commit_changes(&repo_path);
                    last_commit = std::time::Instant::now();
                }
            }
            
            tokio::time::sleep(Duration::from_millis(100)).await;
        }
    });
    
    Ok(WatcherHandle {
        shutdown_tx,
        task_handle,
    })
}

fn commit_changes(repo_path: &PathBuf) {
    // Simple auto-commit implementation
    let output = std::process::Command::new("git")
        .current_dir(repo_path)
        .args(&["add", "."])
        .output();
    
    if output.is_err() {
        return;
    }
    
    let timestamp = chrono::Utc::now().format("%Y-%m-%d %H:%M:%S");
    let _ = std::process::Command::new("git")
        .current_dir(repo_path)
        .args(&["commit", "-m", &format!("Auto-commit at {}", timestamp)])
        .output();
}