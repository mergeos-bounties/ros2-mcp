---
name: ros2-mcp
description: >
  ROS2 graph: topics, nodes, services, TF, actions (mock + live). CLI `ros2-mcp` + MCP stdio serve. Use when the user mentions
  ros2-mcp, /ros2-mcp, or related domain work. One-command Grok install from GitHub.
metadata:
  short-description: "ROS2 graph: topics, nodes, services, TF, actions (mock + liv"
---

# ros2-mcp

## One-command install (Grok)

```bash
pip install "git+https://github.com/mergeos-bounties/ros2-mcp.git" && grok plugin install mergeos-bounties/ros2-mcp --trust
```

Or plugin first, then package:

```bash
grok plugin install mergeos-bounties/ros2-mcp --trust
pip install "git+https://github.com/mergeos-bounties/ros2-mcp.git"
```

Verify:

```bash
ros2-mcp version
ros2-mcp doctor
ros2-mcp demo
ros2-mcp serve   # MCP stdio for hosts
```

## Modes

| Env | Values |
| --- | --- |
| `ROS2_MCP_MODE` | `mock` (default) · `live` |

## MCP

```bash
ros2-mcp serve
```

Config ships in plugin `.mcp.json`. Manual: see repo `examples/`.
