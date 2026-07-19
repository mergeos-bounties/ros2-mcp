# ros2-mcp

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.1.1-0E8A16.svg)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-5319E7.svg)](https://modelcontextprotocol.io)
[![MergeOS](https://img.shields.io/badge/MergeOS-bounties-5319E7.svg)](https://github.com/mergeos-bounties)

**ros2-mcp** is an [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server so AI agents (Grok, Cursor, Claude, …) can **inspect and control ROS2** graphs — topics, nodes, services, TF, actions — without hand-writing every `ros2` CLI call.

**Product:** [mergeos-bounties/ros2-mcp](https://github.com/mergeos-bounties/ros2-mcp)

---

## Install (one command)

### Grok — recommended

```bash
pip install "git+https://github.com/mergeos-bounties/ros2-mcp.git" && grok plugin install mergeos-bounties/ros2-mcp --trust
```

This installs the **Python CLI** (`ros2-mcp`) and the **Grok plugin** (skill + MCP server from `.mcp.json`).

Check:

```bash
ros2-mcp version
ros2-mcp doctor
ros2-mcp demo
grok plugin list
grok mcp list
```

Local clone:

```bash
git clone https://github.com/mergeos-bounties/ros2-mcp.git
cd ros2-mcp
pip install -e ".[dev]"
grok plugin install . --trust
```

### Other agents (stdio MCP)

After `pip install "git+https://github.com/mergeos-bounties/ros2-mcp.git"`, point any MCP host at:

| Field | Value |
| --- | --- |
| command | `ros2-mcp` |
| args | `["serve"]` |
| env | `ROS2_MCP_MODE=mock` |

**Claude Desktop** — merge [examples/claude_desktop_config.json](examples/claude_desktop_config.json) into Claude MCP config.

**Cursor** — merge [examples/cursor_mcp.json](examples/cursor_mcp.json).

**Grok config.toml** (manual, without plugin):

```toml
[mcp_servers.ros2_mcp]
command = "ros2-mcp"
args = ["serve"]
env = { ROS2_MCP_MODE = "mock" }
```

Or one-shot:

```bash
pip install "git+https://github.com/mergeos-bounties/ros2-mcp.git"
grok mcp add ros2-mcp -- ros2-mcp serve
```

## Supported AI agents / hosts

| Agent / Host | MCP support | Setup |
| --- | --- | --- |
| **Grok** (CLI / TUI / Build) | **Yes** | `grok plugin install mergeos-bounties/ros2-mcp --trust` then `pip install "git+https://github.com/mergeos-bounties/ros2-mcp.git"` |
| **Claude Desktop** | **Yes** | Copy [examples/claude_desktop_config.json](examples/claude_desktop_config.json) into Claude MCP settings |
| **Cursor** | **Yes** | Merge [examples/cursor_mcp.json](examples/cursor_mcp.json) into Cursor MCP config |
| **Claude Code** | **Yes** | stdio MCP: same `command`/`args` as Claude Desktop / Grok |
| **VS Code** (MCP / Continue / Cline) | **Yes** | Generic stdio server config pointing at `ros2-mcp serve` |
| **Windsurf / Cascade** | **Yes** | stdio MCP entry with `ros2-mcp` + `serve` |
| **Codex CLI** | **Yes** (stdio) | Register MCP server command `ros2-mcp serve` in Codex MCP settings |
| **ChatGPT Desktop** | **Partial** | Only if host supports custom MCP stdio servers |
| **Gemini CLI** | **Partial** | Only if MCP stdio plugins are enabled |

All packages speak **MCP over stdio** (`ros2-mcp serve`). Default mode is **mock** (offline, no simulator/terminal/GIMP required).

---

## Table of contents

- [Modes](#modes)
- [Highlights](#highlights)
- [Screenshots](#screenshots)
- [Quick start](#quick-start)
- [Docker image](#docker-image)
- [CLI reference](#cli-reference)
- [MCP resources](#mcp-resources)
- [MCP host config](#mcp-host-config)
- [Diagrams](#diagrams)
- [Repository layout](#repository-layout)
- [Development](#development)
- [Host Setup](#host-setup)
- [MergeOS bounties](#mergeos-bounties)
- [License](#license)
- [Configuration](#configuration)
- [IDE Configuration](#ide-configuration)

---

## Modes

All packages ship with **mock mode** as the default.  
Parameter names and `value: "<redacted-live-value>"` so MCP host transcripts
and CI logs do not accidentally capture runtime configuration. Use
`ROS2_MCP_MODE=live` only when a live ROS2 graph is available.

| Feature | Mock | Live |
| --- | ---: | ---: |
| Topic list | ✅ | ✅ |
| Topic echo | ✅ | ✅ |
| Topic publish | ✅ | ✅ |
| Node list | ✅ | ✅ |
| Service list | ✅ | ✅ |
| Service call | ✅ | ✅ |
| TF tree | ✅ | ✅ |
| Actions | ✅ | ✅ |
| **Requires ROS2** | No | Yes |

---

## Highlights

| Capability | Description |
| --- | --- |
| **Offline demo** | `ros2-mcp demo` exercises doctor, topics, pub/echo, spawn, TF, actions |
| **MCP stdio serve** | Plug into agent hosts as an MCP server |
| **One-shot call** | `ros2-mcp call` without a full MCP host |
| **Tool list** | Discover registered MCP tools |

---

## Quick start

```bash
git clone https://github.com/mergeos-bounties/ros2-mcp.git
cd ros2-mcp
pip install -e ".[dev]"
ros2-mcp version
ros2-mcp demo
ros2-mcp tools list
```

---

## Docker image

Build a ROS2 Humble image with `ros2-mcp` installed into an isolated Python
environment:

```bash
docker build -t ros2-mcp:humble .
docker run --rm ros2-mcp:humble demo
```

Serve MCP over stdio from the container:

```bash
docker run --rm -i ros2-mcp:humble serve
```

---

## CLI reference

| Command | Description |
| --- | --- |
| `ros2-mcp version` | Version + mode |
| `ros2-mcp demo` | Offline smoke of core backend APIs |
| `ros2-mcp serve` | MCP server over **stdio** (for hosts) |
| `ros2-mcp serve --verbose` | Same, plus structured JSON tool-call logs on **stderr** |
| `ros2-mcp call …` | One-shot tool call (mock/live) |
| `ros2-mcp tools list` | List MCP tools |
| `ros2-mcp call topic_hz topic=/scan` | Parsed mock topic publish-rate sample |

---

## MCP resources

In addition to tools, the server exposes an **MCP resource template** so hosts can
inspect the ROS2 graph structure.

> Note: the MCP SDK's URI-template matcher binds a single path segment, so a
> `ros2-mcp serve` emits **structured JSON logs to stderr only**. The MCP stdio transport uses **stdout** for the JSON-RPC protocol stream, so any log written to stdout would corrupt the protocol and break the host connection. All logging goes to stderr, leaving stdout clean for MCP.

| Command | Level | Description |
| --- | --- | --- |
| `ros2-mcp serve` | INFO | Lifecycle only: one `serve_start` record (transport, mode, tool count, version) |
| `ros2-mcp serve --verbose` (`-v`) | DEBUG | Per-tool-call records: `tool_call_start`, `tool_call` (with `duration_ms`, `status`), and `tool_call_error` (with traceback) on failure |

```json
{"ts": 1712345678.9, "level": "DEBUG", "logger": "ros2_mcp", "msg": "tool_call", "tool": "ros2_list_topics", "duration_ms": 1.42, "status": "ok"}
```

To capture logs to a file:

```bash
ros2-mcp serve --verbose 2> ros2-mcp.log
```

---

## MCP host config

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

### Architecture

  <img src="docs/diagrams/architecture.svg" alt="ros2-mcp architecture" width="100%" />

### Workflow

  <img src="docs/diagrams/workflow.svg" alt="ros2-mcp workflow" width="100%" />

---

## Repository layout

```
ros2-mcp/
├── src/ros2_mcp/
│   ├── __init__.py
│   ├── server.py          # FastMCP tools
│   ├── mock_backend.py    # Mock ROS2 graph
│   └── live_backend.py    # Live ROS2 graph
├── tests/
├── docs/
├── examples/
├── scripts/
├── .mcp.json
└── pyproject.toml
```

---

## Development

```bash
git clone https://github.com/mergeos-bounties/ros2-mcp.git
cd ros2-mcp
pip install -e ".[dev]"
pytest -q
ruff check src/
ros2-mcp demo
```

---

## MergeOS bounties

Star → claim → PR **master** → MRG **25–200**. Evidence: CLI logs / MCP host config snippets (redact secrets).

---

## License

MIT

---

## Configuration

See [MCP_HOST_CONFIG.md](docs/MCP_HOST_CONFIG.md) for Claude/Cursor setup.

---

## IDE Configuration

- [Cursor MCP Config](docs/CURSOR_MCP_CONFIG.md) — Copy-paste configuration for Cursor IDE with mock/live modes
- [Live vs Mock Safety Matrix](docs/LIVE_VS_MOCK_SAFETY_MATRIX.md) — Safety considerations for live vs mock modes
