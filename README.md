# ros2-mcp

**ros2-mcp** is an [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server so AI agents can **inspect and control ROS2** graphs: topics, nodes, services, parameters, and simple pub/echo — without hand-writing `ros2` CLI each time.

| Mode | When |
| --- | --- |
| **mock** (default) | Offline Windows / CI — seeded demo graph (turtlesim-like + cmd_vel) |
| **live** | Host has ROS2 + `rclpy` — real graph via subprocess `ros2` CLI bridge |

Org: [mergeos-bounties](https://github.com/mergeos-bounties) · MergeOS MRG bounties.

## Why

- AI tools need a **stable tool schema** for robotics work (list → echo → pub → service).
- Full ROS2 on every contributor machine is heavy; **mock mode** is always runnable.
- Pairs with [Lappa](https://github.com/mergeos-bounties/Lappa) (ROS2 package IDE): Lappa for edit/sim UI, ros2-mcp for agent control.

## Quick start

```powershell
cd D:\ThanhTrucSolutions\ros2-mcp
python -m venv .venv
.\.venv\Scripts\activate
pip install -e ".[dev]"

ros2-mcp demo
ros2-mcp tools list
ros2-mcp serve
```

### Wire into Grok / Cursor / Claude Desktop

**Grok** (`~/.grok/config.toml`):

```toml
[mcp_servers.ros2]
command = "ros2-mcp"
args = ["serve"]
# or: command = "python", args = ["-m", "ros2_mcp", "serve"]
enabled = true
```

**Cursor / Claude** example JSON:

```json
{
  "mcpServers": {
    "ros2": {
      "command": "ros2-mcp",
      "args": ["serve"],
      "env": { "ROS2_MCP_MODE": "mock" }
    }
  }
}
```

See [examples/](examples/).

## Khởi động nhanh (Tiếng Việt)

```powershell
cd D:\ThanhTrucSolutions\ros2-mcp
python -m venv .venv
.\.venv\Scripts\activate
pip install -e ".[dev]"

ros2-mcp demo
ros2-mcp tools list
ros2-mcp serve
```

### Kết nối với Grok / Cursor / Claude Desktop

**Grok** (`~/.grok/config.toml`):

```toml
[mcp_servers.ros2]
command = "ros2-mcp"
args = ["serve"]
enabled = true
```

**Cursor / Claude** (ví dụ file JSON):

```json
{
  "mcpServers": {
    "ros2": {
      "command": "ros2-mcp",
      "args": ["serve"],
      "env": { "ROS2_MCP_MODE": "mock" }
    }
  }
}
```

## MCP tools

| Tool | Description |
| --- | --- |
| `ros2_mode` | Get/set backend mode (`mock` / `live`) |
| `ros2_list_topics` | List topics (+ optional types) |
| `ros2_topic_info` | Type, publishers, subscribers |
| `ros2_topic_echo` | Last N messages from buffer / live snapshot |
| `ros2_topic_pub` | Publish JSON payload once or N times |
| `ros2_list_nodes` | List nodes |
| `ros2_node_info` | Pubs/subs/services for a node |
| `ros2_list_services` | List services |
| `ros2_service_call` | Call service with JSON request |
| `ros2_list_params` | List parameters (node optional) |
| `ros2_get_param` / `ros2_set_param` | Parameter get/set |
| `ros2_graph_summary` | Compact graph overview for the model |
| `ros2_tf_tree` | TF frames (mock map→odom→base_link) |
| `ros2_list_actions` / `ros2_action_send_goal` | Actions (mock nav2 + turtlesim) |
| `ros2_doctor` | Environment / connectivity check |
| `ros2_seed_demo` | Reset mock turtlesim-like graph |

## CLI

```text
ros2-mcp demo              # offline smoke of all mock tools
ros2-mcp tools list        # print tool names
ros2-mcp serve             # stdio MCP server (for hosts)
ros2-mcp call list_topics  # one-shot tool call (mock)
```

## Env

| Variable | Default | Meaning |
| --- | --- | --- |
| `ROS2_MCP_MODE` | `mock` | `mock` or `live` |
| `ROS2_MCP_DOMAIN_ID` | `0` | Hint for live ROS_DOMAIN_ID |
| `ROS2_MCP_ROS2_BIN` | `ros2` | Path to ros2 CLI |
| `ROS2_MCP_PUB_ALLOWLIST` | _(empty)_ | Comma topics allowed in **live** publish (safety) |

## Layout

```
src/ros2_mcp/
  server.py       # FastMCP app
  cli.py
  backend/        # mock + live ros2 CLI bridge
  tools/          # tool registration
examples/         # host config snippets
docs/BOUNTY.md
```

## Tests

```powershell
pip install -e ".[dev]"
ruff check src tests
pytest -q
ros2-mcp demo
```

## MergeOS bounties

1. Star this repo + [mergeos](https://github.com/mergeos-bounties/mergeos)
2. Claim a `bounty` issue
3. Claim on MergeOS [issue #1](https://github.com/mergeos-bounties/mergeos/issues/1)
4. PR to **ros2-mcp** with tests
5. Credit MRG 25 / 50 / 100 / 200

See [docs/BOUNTY.md](docs/BOUNTY.md).

## License

MIT
