use std::io::{self, BufRead};
use vibe_git::McpClient;

fn main() {
    let stdin = io::stdin();
    let mut client = McpClient::new();
    for line in stdin.lock().lines() {
        let line = match line {
            Ok(l) => l,
            Err(_) => continue,
        };
        let mut parts = line.split_whitespace();
        match parts.next() {
            Some("start") => {
                if let Some(branch) = parts.next() {
                    client.start_vibing(branch);
                    println!("started {branch}");
                } else {
                    println!("usage: start <branch>");
                }
            }
            Some("stop") => {
                client.stop_vibing();
                println!("stopped");
            }
            Some("status") => {
                if let Some(branch) = client.branch() {
                    println!("vibing on {branch}");
                } else {
                    println!("idle");
                }
            }
            _ => println!("unknown command"),
        }
    }
}
