# ROS2 MCP Server

MCP server for ROS2 interaction - enables AI agents to control ROS2 systems through the Model Context Protocol.

## Installation

```bash
npm install -g @mergeos/ros2-mcp
```

## Quick Start

### With ROS2 Installed

```bash
# Source your ROS2 environment
source /opt/ros/humble/setup.bash

# Start the MCP server
ros2-mcp
```

### Offline/Mock Mode (No ROS2 Required)

For development, testing, or AI agent experimentation without a ROS2 installation:

```bash
# Set mock mode environment variable
export ROS2_MCP_MOCK=true

# Start the server
ros2-mcp
```

In mock mode:
- No ROS2 installation needed
- All ROS2 commands return simulated responses
- Topic lists, node information, and parameter values are mocked
- Useful for developing AI agent behaviors and workflows
- Great for CI/CD pipelines and testing environments

**Mock Mode Limitations:**
- No actual robot control or real sensor data
- Simulated topics and nodes have hardcoded responses
- Cannot connect to real ROS2 systems
- Service calls return placeholder data

## Configuration

### Environment Variables

- `ROS2_MCP_MOCK` - Enable mock mode (default: false)
- `ROS2_MCP_PORT` - Server port (default: 3000)
- `ROS2_DISTRO` - ROS2 distribution (default: humble)

### Claude Desktop Integration

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "ros2": {
      "command": "ros2-mcp",
      "env": {
        "ROS2_MCP_MOCK": "false"
      }
    }
  }
}
```

For mock mode:

```json
{
  "mcpServers": {
    "ros2-mock": {
      "command": "ros2-mcp",
      "env": {
        "ROS2_MCP_MOCK": "true"
      }
    }
  }
}
```

## Usage

### Available Tools

- `ros2_topic_list` - List all active topics
- `ros2_topic_echo` - Subscribe to topic messages
- `ros2_topic_pub` - Publish messages to topics
- `ros2_node_list` - List all active nodes
- `ros2_node_info` - Get detailed node information
- `ros2_param_get` - Get parameter values
- `ros2_param_set` - Set parameter values
- `ros2_service_list` - List available services
- `ros2_service_call` - Call ROS2 services

### Example Agent Workflow

```
Agent: List all topics
Server: [/cmd_vel, /odom, /scan, ...]

Agent: Echo /scan topic
Server: [LaserScan data stream...]

Agent: Publish to /cmd_vel
Server: Message published successfully
```

## Development

```bash
# Clone the repository
git clone https://github.com/mergeos-bounties/ros2-mcp.git
cd ros2-mcp

# Install dependencies
npm install

# Run in development mode with mock
ROS2_MCP_MOCK=true npm run dev

# Run tests
npm test

# Build
npm run build
```

## Testing AI Agents

Mock mode is ideal for testing AI agent behaviors:

1. **Develop agent logic** without needing ROS2 hardware
2. **Test error handling** with predictable responses
3. **CI/CD integration** - run tests in environments without ROS2
4. **Rapid prototyping** - iterate on agent behaviors quickly

Example test scenario:

```bash
# Terminal 1: Start mock server
ROS2_MCP_MOCK=true ros2-mcp

# Terminal 2: Connect your AI agent
# Agent will receive simulated ROS2 data
# Perfect for development and testing
```

## Architecture

- Built on Model Context Protocol (MCP)
- Wraps ROS2 CLI commands
- Provides structured JSON responses
- Supports both real and simulated ROS2 environments

## Requirements

### Real Mode
- ROS2 Humble or later
- Node.js 18+
- Linux (Ubuntu 22.04 recommended)

### Mock Mode
- Node.js 18+
- Any OS (Linux, macOS, Windows)
- No ROS2 installation needed

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT

## Bounty Program

This project is part of the MergeOS bounty program. To claim bounties:

1. Follow https://github.com/mergeos-bounties
2. Star https://github.com/mergeos-bounties/mergeos
3. Star https://github.com/mergeos-bounties/mergeos-contract

## Support

- Issues: https://github.com/mergeos-bounties/ros2-mcp/issues
- Discord: [MergeOS Community](https://discord.gg/mergeos)