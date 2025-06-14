use anyhow::Result;
use rmcp::{model::ServerInfo, schemars, tool, ServerHandler};
use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use std::sync::{Arc, Mutex};
use crate::{VibeSession, Idle, Vibing};

/// The vibe-git MCP service
#[derive(Debug, Clone)]
pub struct VibeGitService {
    repo_path: PathBuf,
    session: Arc<Mutex<Option<SessionHolder>>>,
}

#[derive(Debug)]
enum SessionHolder {
    Idle(VibeSession<Idle>),
    Vibing {
        session: VibeSession<Vibing>,
        branch_name: String,
    },
}

impl VibeGitService {
    pub fn new(repo_path: PathBuf) -> Result<Self> {
        let session = VibeSession::new(repo_path.clone())?;
        Ok(Self {
            repo_path,
            session: Arc::new(Mutex::new(Some(SessionHolder::Idle(session)))),
        })
    }
}

#[derive(Debug, Serialize, Deserialize, schemars::JsonSchema)]
pub struct StartVibingRequest {}

#[derive(Debug, Serialize, Deserialize, schemars::JsonSchema)]
pub struct StopVibingRequest {
    pub commit_message: String,
}

#[derive(Debug, Serialize, Deserialize, schemars::JsonSchema)]
pub struct VibeStatusRequest {}

#[tool(tool_box)]
impl VibeGitService {
    #[tool(description = "🚀 CALL THIS FIRST before making any code changes! Creates a new git branch and starts auto-committing all file changes every second. Safe to call multiple times - will not create duplicate sessions.")]
    async fn start_vibing(&self, #[tool(aggr)] _request: StartVibingRequest) -> String {
        let mut session_lock = self.session.lock().unwrap();
        
        match session_lock.as_ref() {
            Some(SessionHolder::Vibing { .. }) => {
                // Already vibing - idempotent response
                "Already vibing! Session is active and auto-committing changes.".to_string()
            }
            _ => {
                // Start vibing
                if let Some(SessionHolder::Idle(session)) = session_lock.take() {
                    match session.start_vibing() {
                        Ok((vibing_session, branch_name)) => {
                            *session_lock = Some(SessionHolder::Vibing {
                                session: vibing_session,
                                branch_name,
                            });
                            "🚀 Started vibing! New branch created and auto-committing all changes every second.".to_string()
                        }
                        Err(e) => {
                            // Need to recreate session since start_vibing consumes it
                            if let Ok(new_session) = VibeSession::new(self.repo_path.clone()) {
                                *session_lock = Some(SessionHolder::Idle(new_session));
                            }
                            format!("Error starting vibe: {}", e)
                        }
                    }
                } else {
                    // Session doesn't exist - create new one
                    match VibeSession::new(self.repo_path.clone()) {
                        Ok(session) => {
                            match session.start_vibing() {
                                Ok((vibing_session, branch_name)) => {
                                    *session_lock = Some(SessionHolder::Vibing {
                                        session: vibing_session,
                                        branch_name,
                                    });
                                    "🚀 Started vibing! New branch created and auto-committing all changes every second.".to_string()
                                }
                                Err(e) => format!("Error starting vibe: {}", e)
                            }
                        }
                        Err(e) => format!("Error creating session: {}", e)
                    }
                }
            }
        }
    }

    #[tool(description = "🏁 Call this when you're done making changes. Squashes all auto-commits into a single commit with your message, rebases onto latest main, and creates a PR. Safe to call even if not vibing.")]
    async fn stop_vibing(&self, #[tool(aggr)] request: StopVibingRequest) -> String {
        let mut session_lock = self.session.lock().unwrap();
        
        match session_lock.as_ref() {
            Some(SessionHolder::Idle(_)) => {
                // Not vibing - idempotent response
                "Not currently vibing - no active session to stop. Call start_vibing first if you want to begin a new session.".to_string()
            }
            Some(SessionHolder::Vibing { .. }) => {
                if let Some(SessionHolder::Vibing { session, branch_name }) = session_lock.take() {
                    match session.stop_vibing(branch_name, request.commit_message.clone()) {
                        Ok(idle_session) => {
                            *session_lock = Some(SessionHolder::Idle(idle_session));
                            format!("🏁 Stopped vibing! Squashed commits, rebased on main, and created PR with message: '{}'", request.commit_message)
                        }
                        Err(e) => format!("Error stopping vibe: {}", e)
                    }
                } else {
                    "Error: Could not access vibing session".to_string()
                }
            }
            None => {
                // No session exists - idempotent response
                "No active session. Call start_vibing first to begin working.".to_string()
            }
        }
    }

    #[tool(description = "📊 Check the current vibe session status - whether you're currently vibing or idle. Use this to understand the current state.")]
    async fn vibe_status(&self, #[tool(aggr)] _request: VibeStatusRequest) -> String {
        let session_lock = self.session.lock().unwrap();
        
        match session_lock.as_ref() {
            Some(SessionHolder::Vibing { .. }) => {
                "🟢 VIBING: Active session running! Auto-committing all file changes every second. Call stop_vibing(commit_message) when done.".to_string()
            }
            Some(SessionHolder::Idle(_)) => {
                "🔵 IDLE: Ready to start vibing. Call start_vibing() to begin auto-committing changes.".to_string()
            }
            None => {
                "⚪ NOT INITIALIZED: No session exists. Call start_vibing() to begin.".to_string()
            }
        }
    }
}

#[tool(tool_box)]
impl ServerHandler for VibeGitService {
    fn get_info(&self) -> ServerInfo {
        ServerInfo {
            instructions: Some(
                "vibe-git MCP Server - enables friction-free git workflows for vibe coding. \
                 Always call start_vibing() before making code changes, then stop_vibing(commit_message) when done."
                    .into(),
            ),
            ..Default::default()
        }
    }
}