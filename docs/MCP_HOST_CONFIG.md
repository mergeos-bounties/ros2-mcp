# MCP Host Configuration

Use `mock` mode by default when registering `ros2-mcp` in Cursor,
Claude Desktop, or another stdio MCP host. Mock mode does not require a ROS2
installation and avoids touching a live robot graph while you confirm the host
configuration.

## Cursor

Merge this snippet into Cursor's MCP settings:

```json
{
  "mcpServers": {
    "ros2-mcp": {
      "command": "ros2-mcp",
      "args": ["serve"],
      "env": {
        "ROS2_MCP_MODE": "mock"
      }
    }
  }
}
```

The same JSON is available at
[`examples/cursor_mcp.json`](../examples/cursor_mcp.json).

## Claude Desktop

Use the same stdio server shape in `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ros2-mcp": {
      "command": "ros2-mcp",
      "args": ["serve"],
      "env": {
        "ROS2_MCP_MODE": "mock"
      }
    }
  }
}
```

## Live Mode

Only switch to live mode on a host where ROS2 is installed and sourced:

```json
{
  "mcpServers": {
    "ros2-mcp": {
      "command": "ros2-mcp",
      "args": ["serve"],
      "env": {
        "ROS2_MCP_MODE": "live"
      }
    }
  }
}
```

Live mode reads the real ROS graph through `ros2` CLI calls. Keep secrets out of
host config files and transcripts; live parameter listing redacts values by
default, but explicit single-parameter reads should still be treated as
sensitive.
