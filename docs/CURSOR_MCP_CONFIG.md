# Cursor MCP Configuration for ros2-mcp

Copy-paste configuration for using ros2-mcp with Cursor IDE.

## Quick Setup

1. Open Cursor settings (Cmd+, / Ctrl+,)
2. Navigate to **Features** → **Claude Code** → **MCP Servers**
3. Add the following configuration:

```json
{
  "mcpServers": {
    "ros2-mcp": {
      "command": "npx",
      "args": ["-y", "@mergeos/ros2-mcp"],
      "env": {
        "ROS2_MCP_MODE": "mock"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## Mock Mode (Recommended for Development)

```json
{
  "mcpServers": {
    "ros2-mcp": {
      "command": "npx",
      "args": ["-y", "@mergeos/ros2-mcp"],
      "env": {
        "ROS2_MCP_MODE": "mock",
        "ROS2_MCP_MOCK_TOPICS": "/topic1,/topic2,/topic3"
      }
    }
  }
}
```

## Live Mode (Production)

```json
{
  "mcpServers": {
    "ros2-mcp": {
      "command": "npx",
      "args": ["-y", "@mergeos/ros2-mcp"],
      "env": {
        "ROS2_MCP_MODE": "live",
        "ROS2_MCP_MASTER_URI": "http://localhost:11311"
      }
    }
  }
}
```

## Available Tools

| Tool | Description |
|------|-------------|
| `ros2_topic_list` | List all available ROS2 topics |
| `ros2_topic_echo` | Echo messages from a specific topic |
| `ros2_topic_publish` | Publish a message to a topic |
| `ros2_node_list` | List all running ROS2 nodes |
| `ros2_service_list` | List available ROS2 services |
| `ros2_service_call` | Call a ROS2 service |
