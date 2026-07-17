# Host Setup Guide

This guide provides OS-specific instructions for setting up ROS2-MCP with various AI agent hosts.

## Supported Hosts

- [Grok](#grok)
- [Claude Desktop](#claude-desktop)
- [Cursor](#cursor)
- [VS Code (with MCP extension)](#vscode-mcp-extension)
- [Windsurf / Cascade](#windsurf--cascade)
- [Codex CLI](#codex-cli)

## Operating System Notes

### Linux/macOS

- Use the standard `ros2-mcp` command.
- Ensure you have Python 3.11+ installed.
- For live mode, you need a working ROS2 installation.

### Windows

- Use the same `ros2-mcp` command (ensure it's in your PATH).
- Set environment variables using `set` in Command Prompt or `$env:` in PowerShell.
- The MCP server works the same way; ensure you have the Python executable from the virtual environment in your PATH.

---

## Grok

### Prerequisites
- Install the ros2-mcp package: `pip install "git+https://github.com/mergeos-bounties/ros2-mcp.git"`
- Install the Grok plugin: `grok plugin install mergeos-bounties/ros2-mcp --trust`

### Configuration
No additional configuration is needed. The plugin will use the `ros2-mcp` command with `serve` arguments.

### Example
```bash
# Install the package
pip install "git+https://github.com/mergeos-bounties/ros2-mcp.git"
# Install the plugin
grok plugin install mergeos-bounties/ros2-mcp --trust
# Now you can use ros2-mcp within Grok
```

## Claude Desktop

### Prerequisites
- Install the ros2-mcp package: `pip install "git+https://github.com/mergeos-bounties/ros2-mcp.git"`
- Copy the example configuration file to your Claude MCP settings.

### Configuration
1. Copy `examples/claude_desktop_config.json` to your Claude MCP configuration directory.
   - On Linux: `~/.claude/claude_desktop_config.json`
   - On macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - On Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. Ensure the `command` points to your `ros2-mcp` executable (if not in PATH, use the full path).

### Example Configuration
See `examples/claude_desktop_config.json`.

## Cursor

### Prerequisites
- Install the ros2-mcp package: `pip install "git+https://github.com/mergeos-bounties/ros2-mcp.git"`

### Configuration
1. Copy `examples/cursor_mcp.json` to your Cursor MCP settings.
   - The location varies by OS; check Cursor's documentation for MCP settings.
2. Ensure the `command` points to your `ros2-mcp` executable.

### Example Configuration
See `examples/cursor_mcp.json`.

## VS Code (MCP Extension)

### Prerequisites
- Install the ros2-mcp package: `pip install "git+https://github.com/mergeos-bounties/ros2-mcp.git"`
- Install the "MCP" extension from the VS Code marketplace.

### Configuration
1. Open the extension settings and add a new MCP server.
2. Set the command to `ros2-mcp` and args to `["serve"]`.
3. Optionally set the environment variable `ROS2_MCP_MODE` to `mock` or `live`.

## Windsurf / Cascade

### Prerequisites
- Install the ros2-mcp package: `pip install "git+https://github.com/mergeos-bounties/ros2-mcp.git"`

### Configuration
- Add an MCP server configuration with:
  - Command: `ros2-mcp`
  - Arguments: `["serve"]`
  - Environment: `{ "ROS2_MCP_MODE": "mock" }` (or `live` if you have ROS2)

## Codex CLI

### Prerequisites
- Install the ros2-mcp package: `pip install "git+https://github.com/mergeos-bounties/ros2-mcp.git"`

### Configuration
- In your Codex MCP settings, add a server with:
  - Command: `ros2-mcp`
  - Arguments: `["serve"]`
  - Environment: `{ "ROS2_MCP_MODE": "mock" }`

## Verification

After configuring your host, you should be able to:
1. See the ros2-mcp server listed in your host's MCP server list.
2. Use tools like `ros2_mcp_list_topics`, `ros2_mcp_echo`, etc.
3. Run the demo: `ros2-mcp demo` (should work in mock mode).

## Troubleshooting

- If the server fails to start, check that `ros2-mcp` is in your PATH or provide the full path.
- Ensure you have Python 3.11+ and the required dependencies installed.
- For live mode, source your ROS2 setup before starting the server.

