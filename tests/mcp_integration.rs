use std::process::Command;
use tempfile::TempDir;
use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader};
use tokio::process::{Child, Command as TokioCommand};
use serde_json::Value;
use anyhow::Result;

struct McpTestClient {
    process: Child,
    repo_path: TempDir,
}

impl McpTestClient {
    async fn new() -> Result<Self> {
        // Create test repository
        let temp_dir = TempDir::new()?;
        let repo_path = temp_dir.path();
        
        // Initialize git repo
        Command::new("git")
            .current_dir(repo_path)
            .args(&["init"])
            .output()?;
            
        Command::new("git")
            .current_dir(repo_path)
            .args(&["config", "user.name", "Test User"])
            .output()?;
            
        Command::new("git")
            .current_dir(repo_path)
            .args(&["config", "user.email", "test@example.com"])
            .output()?;
            
        // Create initial commit
        std::fs::write(repo_path.join("README.md"), "# Test Repository")?;
        Command::new("git")
            .current_dir(repo_path)
            .args(&["add", "README.md"])
            .output()?;
            
        Command::new("git")
            .current_dir(repo_path)
            .args(&["commit", "-m", "Initial commit"])
            .output()?;
        
        // Start the MCP server (use the built binary)
        let mut process = TokioCommand::new("./target/debug/vibe-git")
            .args(&[repo_path.to_str().unwrap()])
            .stdin(std::process::Stdio::piped())
            .stdout(std::process::Stdio::piped())
            .stderr(std::process::Stdio::piped())
            .spawn()?;
            
        // Give the server time to start
        tokio::time::sleep(tokio::time::Duration::from_millis(500)).await;
        
        Ok(McpTestClient {
            process,
            repo_path: temp_dir,
        })
    }
    
    async fn send_request(&mut self, method: &str, params: Option<Value>) -> Result<Value> {
        let request = serde_json::json!({
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        });
        
        let request_line = format!("{}\n", serde_json::to_string(&request)?);
        
        if let Some(stdin) = self.process.stdin.as_mut() {
            stdin.write_all(request_line.as_bytes()).await?;
            stdin.flush().await?;
        }
        
        if let Some(stdout) = self.process.stdout.as_mut() {
            let mut reader = BufReader::new(stdout);
            let mut response_line = String::new();
            reader.read_line(&mut response_line).await?;
            
            let response: Value = serde_json::from_str(&response_line)?;
            Ok(response)
        } else {
            Err(anyhow::anyhow!("No stdout available"))
        }
    }
    
    async fn initialize(&mut self) -> Result<()> {
        let params = serde_json::json!({
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        });
        
        let response = self.send_request("initialize", Some(params)).await?;
        
        if let Some(error) = response.get("error") {
            if !error.is_null() {
                return Err(anyhow::anyhow!("Initialization failed: {:?}", error));
            }
        }
        
        Ok(())
    }
    
    async fn list_tools(&mut self) -> Result<Vec<Value>> {
        let response = self.send_request("tools/list", Some(serde_json::json!({}))).await?;
        
        if let Some(error) = response.get("error") {
            if !error.is_null() {
                return Err(anyhow::anyhow!("List tools failed: {:?}", error));
            }
        }
        
        let tools = response["result"]["tools"].as_array()
            .ok_or_else(|| anyhow::anyhow!("Expected tools array"))?;
            
        Ok(tools.clone())
    }
    
    async fn call_tool(&mut self, name: &str, arguments: Option<Value>) -> Result<Value> {
        let params = serde_json::json!({
            "name": name,
            "arguments": arguments.unwrap_or(serde_json::json!({}))
        });
        
        let response = self.send_request("tools/call", Some(params)).await?;
        
        if let Some(error) = response.get("error") {
            if !error.is_null() {
                return Err(anyhow::anyhow!("Tool call failed: {:?}", error));
            }
        }
        
        Ok(response["result"].clone())
    }
}

impl Drop for McpTestClient {
    fn drop(&mut self) {
        let _ = self.process.kill();
    }
}

#[tokio::test]
async fn test_mcp_initialization() -> Result<()> {
    let mut client = McpTestClient::new().await?;
    
    client.initialize().await?;
    
    Ok(())
}

#[tokio::test]
async fn test_mcp_list_tools() -> Result<()> {
    let mut client = McpTestClient::new().await?;
    client.initialize().await?;
    
    let tools = client.list_tools().await?;
    
    assert_eq!(tools.len(), 3);
    
    let tool_names: Vec<&str> = tools.iter()
        .map(|tool| tool["name"].as_str().unwrap())
        .collect();
        
    assert!(tool_names.contains(&"start_vibing"));
    assert!(tool_names.contains(&"stop_vibing"));
    assert!(tool_names.contains(&"vibe_status"));
    
    Ok(())
}

#[tokio::test]
async fn test_mcp_vibe_status_idle() -> Result<()> {
    let mut client = McpTestClient::new().await?;
    client.initialize().await?;
    
    let result = client.call_tool("vibe_status", None).await?;
    
    let content = &result["content"][0]["text"];
    assert!(content.as_str().unwrap().contains("🔵 IDLE"));
    
    Ok(())
}

#[tokio::test]
async fn test_mcp_start_vibing() -> Result<()> {
    let mut client = McpTestClient::new().await?;
    client.initialize().await?;
    
    let result = client.call_tool("start_vibing", None).await?;
    
    let content = &result["content"][0]["text"];
    assert!(content.as_str().unwrap().contains("🚀 Started vibing"));
    
    Ok(())
}

#[tokio::test]
async fn test_mcp_full_workflow() -> Result<()> {
    let mut client = McpTestClient::new().await?;
    client.initialize().await?;
    
    // 1. Check initial status
    let status = client.call_tool("vibe_status", None).await?;
    assert!(status["content"][0]["text"].as_str().unwrap().contains("🔵 IDLE"));
    
    // 2. Start vibing
    let start_result = client.call_tool("start_vibing", None).await?;
    assert!(start_result["content"][0]["text"].as_str().unwrap().contains("🚀 Started vibing"));
    
    // 3. Check status after starting
    let status = client.call_tool("vibe_status", None).await?;
    assert!(status["content"][0]["text"].as_str().unwrap().contains("🟢 VIBING"));
    
    // 4. Stop vibing
    let stop_args = serde_json::json!({
        "commit_message": "Test commit from integration test"
    });
    let stop_result = client.call_tool("stop_vibing", Some(stop_args)).await?;
    assert!(stop_result["content"][0]["text"].as_str().unwrap().contains("🏁 Stopped vibing"));
    
    // 5. Check final status
    let status = client.call_tool("vibe_status", None).await?;
    assert!(status["content"][0]["text"].as_str().unwrap().contains("🔵 IDLE"));
    
    Ok(())
}

#[tokio::test]
async fn test_mcp_idempotent_start_vibing() -> Result<()> {
    let mut client = McpTestClient::new().await?;
    client.initialize().await?;
    
    // Start vibing first time
    let result1 = client.call_tool("start_vibing", None).await?;
    assert!(result1["content"][0]["text"].as_str().unwrap().contains("🚀 Started vibing"));
    
    // Start vibing second time - should be idempotent
    let result2 = client.call_tool("start_vibing", None).await?;
    assert!(result2["content"][0]["text"].as_str().unwrap().contains("Already vibing"));
    assert_eq!(result2["isError"], false);
    
    Ok(())
}

#[tokio::test]
async fn test_mcp_idempotent_stop_vibing() -> Result<()> {
    let mut client = McpTestClient::new().await?;
    client.initialize().await?;
    
    let stop_args = serde_json::json!({
        "commit_message": "Test commit"
    });
    
    // Stop vibing when not vibing - should be idempotent
    let result = client.call_tool("stop_vibing", Some(stop_args)).await?;
    assert!(result["content"][0]["text"].as_str().unwrap().contains("Not currently vibing"));
    assert_eq!(result["isError"], false);
    
    Ok(())
}

#[tokio::test]
async fn test_mcp_tool_descriptions() -> Result<()> {
    let mut client = McpTestClient::new().await?;
    client.initialize().await?;
    
    let tools = client.list_tools().await?;
    
    // Check that all tools have helpful descriptions
    for tool in tools {
        let description = tool["description"].as_str().unwrap();
        assert!(!description.is_empty());
        
        match tool["name"].as_str().unwrap() {
            "start_vibing" => {
                assert!(description.contains("🚀"));
                assert!(description.contains("FIRST"));
            }
            "stop_vibing" => {
                assert!(description.contains("🏁"));
                assert!(description.contains("done"));
            }
            "vibe_status" => {
                assert!(description.contains("📊"));
                assert!(description.contains("status"));
            }
            _ => {}
        }
    }
    
    Ok(())
}