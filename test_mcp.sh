#!/bin/bash

# Test the new MCP implementation
(
    echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}}'
    echo '{"jsonrpc": "2.0", "method": "notifications/initialized"}'
    echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/list"}'
    sleep 0.1
) | ./target/debug/vibe-git-mcp