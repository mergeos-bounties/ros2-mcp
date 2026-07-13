# ros2-mcp

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.1.1-0E8A16.svg)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-5319E7.svg)](https://modelcontextprotocol.io)
[![MergeOS](https://img.shields.io/badge/MergeOS-bounties-5319E7.svg)](https://github.com/mergeos-bounties)

**ros2-mcp** is an [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server so AI agents (Grok, Cursor, Claude, …) can **inspect and control ROS2** graphs — topics, nodes, services, TF, actions — without hand-writing every `ros2` CLI call.

**Product:** [mergeos-bounties/ros2-mcp](https://github.com/mergeos-bounties/ros2-mcp)

---

## Table of contents

- [Modes](#modes)
- [Highlights](#highlights)
- [Screenshots](#screenshots)
- [Quick start](#quick-start)
- [CLI reference](#cli-reference)
- [MCP host config](#mcp-host-config)
- [Diagrams](#diagrams)
- [Repository layout](#repository-layout)
- [Development](#development)
- [MergeOS bounties](#mergeos-bounties)
- [License](#license)

---

## Modes

| Mode | When | Behavior |
| --- | --- | --- |
| **mock** (default) | Windows / CI / no ROS2 install | Seeded turtlesim-like graph: topics, pub, echo, services, TF, actions |
| **live** | Host has ROS2 + CLI | Real graph via `ros2` subprocess bridge (secrets redacted in logs) |

---

## Highlights

| Capability | Description |
| --- | --- |
| **Offline demo** | `ros2-mcp demo` exercises doctor, topics, pub/echo, spawn, TF, actions |
| **MCP stdio serve** | Plug into agent hosts as an MCP server |
| **One-shot call** | `ros2-mcp call` without a full MCP host |
| **Tool list** | Discover registered MCP tools |
| **Lappa-friendly** | Complements [Lappa](https://github.com/mergeos-bounties/Lappa) package IDE workflows |

---

## Screenshots

| Mock graph | Pub + echo |
| :---: | :---: |
| ![Graph](docs/screenshots/demo-graph.png) | ![Topics](docs/screenshots/demo-topics.png) |
| *Seeded graph / doctor* | *cmd_vel pub + pose echo* |

---

## Quick start

```powershell
cd ros2-mcp
python -m venv .venv
.\.venv\Scripts\activate
pip install -e ".[dev]"

ros2-mcp version
ros2-mcp demo
ros2-mcp tools list
```

Mock mode needs **no** ROS2 install.

---

## CLI reference

| Command | Purpose |
| --- | --- |
| `ros2-mcp version` | Version + mode |
| `ros2-mcp demo` | Offline smoke of core backend APIs |
| `ros2-mcp serve` | MCP server over **stdio** (for hosts) |
| `ros2-mcp call …` | One-shot tool call (mock/live) |
| `ros2-mcp tools list` | List MCP tools |

```powershell
# MCP for Cursor / Claude / Grok-compatible hosts
ros2-mcp serve
```

---

## MCP host config

Example stdio server entry (adjust path to your venv):

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

Set `ROS2_MCP_MODE=live` only on machines with a working ROS2 environment.

---

## Diagrams

System architecture and workflow — full width. Open the HTML files for **dark/light theme** and export (PNG/SVG).

### Architecture

[Open interactive diagram](docs/diagrams/architecture.html)

<p align="center">
  <img src="docs/diagrams/architecture.svg" alt="ros2-mcp architecture" width="100%" />
</p>

### Workflow

[Open interactive diagram](docs/diagrams/workflow.html)

<p align="center">
  <img src="docs/diagrams/workflow.svg" alt="ros2-mcp workflow" width="100%" />
</p>

*Generated with [archify](https://github.com/tt-a1i).*

---

## Repository layout

```text
AI agent (MCP host)
        │ stdio
        ▼
   ros2-mcp server
        │
   ┌────┴────┐
   │ mock    │  seeded graph (CI / Windows)
   │ live    │  ros2 CLI subprocess bridge
   └─────────┘

src/ros2_mcp/
  cli.py
  backend/     # mock + live backends
  server.py    # FastMCP tools
docs/screenshots/
docs/diagrams/
```

---

## Development

```powershell
pytest -q
ruff check src tests
ros2-mcp demo
```

Live mode tests should mock subprocesses — CI must not require a ROS2 distro.

---

## MergeOS bounties

Tools for actions/TF, live parsers, Lappa HTTP bridge, publish allowlists.  
Star → claim → PR **master** → MRG **25–200**. Evidence: CLI logs / MCP host config snippets (redact secrets).

---

## License

MIT · MergeOS / ThanhTrucSolutions
