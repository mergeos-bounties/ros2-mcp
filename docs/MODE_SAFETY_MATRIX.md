# Live vs Mock Mode Safety Matrix

Use this matrix when deciding whether a tool call can run in offline `mock`
mode, requires a live ROS2 graph, or needs redaction before evidence is shared
in an MCP host transcript, issue, or pull request.

| Tool or workflow | Mock mode | Live mode | Redaction rule |
| --- | --- | --- | --- |
| `ros2_doctor` | Safe; reports mock backend health and seeded graph counts. | Safe; reports CLI availability and bounded environment metadata. | Do not paste machine-specific paths or hostnames if they identify a private system. |
| `ros2_graph_summary` | Safe; summarizes seeded topics, nodes, services, actions, and pose. | Requires a sourced ROS2 environment; reads the real graph. | Review topic, node, and service names for customer, project, or facility identifiers. |
| `ros2_list_topics` | Safe; returns seeded topic names and types. | Reads live topic names and types through `ros2 topic list`. | Redact topic names that reveal private project names, locations, robots, or people. |
| `ros2_topic_echo` | Safe for seeded mock topics and bounded counts. | Reads live topic payloads. | Treat payloads as sensitive; redact coordinates, IDs, images, maps, credentials, and operational state before sharing. |
| `ros2_topic_pub` | Safe in mock mode; mutates only the in-memory graph. | Writes to a live topic. | Use only with an explicit allowlist and never include secrets in message JSON. |
| `ros2_list_nodes` | Safe; returns seeded node names. | Reads live node names. | Redact names that identify private systems, facilities, or customers. |
| `ros2_node_info` | Safe for mock nodes. | Reads publishers, subscribers, and services for a live node. | Redact private graph names and any operational topology that should not be public. |
| `ros2_list_services` | Safe; returns seeded service names and types. | Reads live service names and types. | Redact private service names and avoid exposing privileged control surfaces. |
| `ros2_service_call` | Safe only for mock/demo services or explicitly allowed calls. | Can mutate a live graph. | Use an allowlist; do not paste request or response fields containing tokens, keys, coordinates, or private IDs. |
| `ros2_list_params` | Safe; returns seeded parameter names and values. | Lists live parameter names with values redacted by default. | Keep `<redacted-live-value>` in shared evidence; review parameter names for secrets. |
| `ros2_get_param` | Safe for mock values. | Reads one explicit live parameter value. | Treat the returned value as sensitive by default; do not paste secrets, paths, credentials, or operational constants. |
| `ros2_set_param` | Safe in mock mode; mutates only in-memory values. | Writes a live parameter. | Require explicit operator intent; do not share sensitive before/after values. |
| `ros2_tf_tree` | Safe; returns a static mock tree. | Reads live TF output where available. | Redact frame names that reveal private robot, site, or payload identifiers. |
| `ros2_bag_info` | Safe for the mock fixture. | Reads metadata for a real bag path. | Redact file paths, dataset names, timestamps, and topic names that identify private deployments. |
| `ros2_list_actions` | Safe; returns seeded action servers. | Reads live action names when supported. | Redact action names that expose private control flows. |
| `ros2_action_send_goal` | Safe in mock mode; returns a simulated success. | Sends a live action goal. | Require explicit operator intent; never paste private goal coordinates, IDs, or mission details. |
| `ros2_lappa_pose` / `ros2_lappa_cmd_vel` | Depends on local Lappa mock/sim endpoint. | Talks to a local HTTP bridge. | Do not share private endpoint URLs, poses, or command payloads without review. |

## Default Evidence Rules

- Prefer `ROS2_MCP_MODE=mock` for public screenshots, issue comments, and PR
  evidence.
- Keep live-mode evidence minimal: command name, high-level result, and redacted
  samples only.
- Do not share raw live topic payloads, bag paths, parameter values, service
  requests, action goals, hostnames, IP addresses, credentials, tokens, maps, or
  customer/project identifiers.
- If a live command mutates state (`pub`, `service_call`, `set_param`,
  `action_send_goal`), require an explicit operator-approved allowlist before
  running it.
