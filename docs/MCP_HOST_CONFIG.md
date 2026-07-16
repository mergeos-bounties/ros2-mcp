# MCP Host Configuration

To register `ros2-mcp` in Claude Desktop or Cursor (mock mode by default for safety), use the following configuration snippet:

```json
{
  "mcpServers": {
    "ros2-mcp": {
      "command": "python",
      "args": ["-m", "ros2_mcp", "--mock"],
      "env": {}
    }
  }
}
```

Add this to your `claude_desktop_config.json` or Cursor MCP settings.
