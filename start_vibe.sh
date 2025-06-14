#!/bin/bash

# Start vibing session
(
    echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}}'
    echo '{"jsonrpc": "2.0", "method": "notifications/initialized"}'
    echo '{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "start_vibing", "arguments": {}}}'
    sleep 0.1
) | ./target/debug/vibe-git-mcp