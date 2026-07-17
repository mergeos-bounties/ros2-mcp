"""FastMCP server: ROS2 tools for AI agents."""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import FastMCP

from ros2_mcp import __version__
from ros2_mcp.backend import get_backend, switch_mode
from ros2_mcp.config import get_mode
from ros2_mcp.logging_config import configure_logging, get_logger, log_tool_call

mcp = FastMCP(
    "ros2-mcp",
    instructions=(
        "ROS2 MCP server. Prefer mock mode offline. "
        "Typical flow: ros2_doctor → ros2_graph_summary → ros2_list_topics → "
        "ros2_topic_echo / ros2_topic_pub. Use JSON for message fields."
    ),
)


def _j(data: Any) -> str:
    return json.dumps(data, indent=2, default=str)


@mcp.tool()
def ros2_mode(mode: str | None = None) -> str:
    """Get or set ROS2 backend mode.

    Args:
        mode: Optional 'mock' or 'live'. Omit to only read current mode.
    """
    if mode:
        return _j(switch_mode(mode))
    b = get_backend()
    return _j({"mode": get_mode(), "backend": b.name, "doctor": b.doctor()})


@mcp.tool()
def ros2_doctor() -> str:
    """Check ROS2 / mock connectivity and environment."""
    return _j(get_backend().doctor())


@mcp.tool()
def ros2_seed_demo() -> str:
    """Reset the mock turtlesim-like graph (mock mode only)."""
    return _j(get_backend().seed_demo())


@mcp.tool()
def ros2_list_topics() -> str:
    """List ROS2 topics and message types."""
    return _j(get_backend().list_topics())


@mcp.tool()
def ros2_topic_info(topic: str) -> str:
    """Detailed info for a topic (type, pubs, subs).

    Args:
        topic: Fully qualified topic name, e.g. /cmd_vel
    """
    return _j(get_backend().topic_info(topic))


@mcp.tool()
def ros2_topic_echo(topic: str, count: int = 1) -> str:
    """Echo recent messages from a topic.

    Args:
        topic: Topic name
        count: Number of messages (1-20 mock, 1-10 live)
    """
    return _j(get_backend().topic_echo(topic, count=count))


@mcp.tool()
def ros2_topic_hz(topic: str | None = None) -> str:
    """Parse/report topic publish rates.

    Args:
        topic: Optional topic name. Mock mode supports /scan and /odom samples.
    """
    return _j(get_backend().topic_hz(topic))


@mcp.resource("topic://{topic_name}")
def topic_resource(topic_name: str) -> str:
    """Snapshot of a ROS2 topic: type, pub/sub counts, and last buffered messages.

    Addressable via the MCP resources protocol using a ``topic://<name>`` URI,
    e.g. ``topic://clock`` or ``topic://scan`` (leading slash optional;
    normalized internally). Note: the MCP SDK's URI template matcher binds a
    single path segment, so namespaced topics containing '/' (e.g.
    ``/turtle1/pose``) cannot be addressed via a literal ``topic://`` URI read
    but are fully supported when this resource function is invoked directly
    (e.g. from in-process code or tests).
    """
    topic = topic_name if topic_name.startswith("/") else f"/{topic_name}"
    backend = get_backend()
    info = backend.topic_info(topic)
    if not info.get("ok", True) and "error" in info:
        return _j({"ok": False, "topic": topic, "error": info["error"]})
    messages = backend.topic_echo(topic, count=5)
    return _j(
        {
            "ok": True,
            "uri": f"topic://{topic.lstrip('/')}",
            "topic": topic,
            "type": info.get("type"),
            "publishers": info.get("publishers"),
            "subscribers": info.get("subscribers"),
            "mode": get_mode(),
            "messages": messages,
        }
    )


@mcp.tool()
def ros2_topic_pub(
    topic: str,
    msg_type: str,
    data_json: str,
    times: int = 1,
) -> str:
    """Publish a message to a topic.

    Args:
        topic: Topic name e.g. /turtle1/cmd_vel
        msg_type: Type e.g. geometry_msgs/msg/Twist
        data_json: JSON object body of the message
        times: Publish count (mock integrates cmd_vel into pose)
    """
    try:
        data = json.loads(data_json) if data_json.strip() else {}
    except json.JSONDecodeError as e:
        return _j({"ok": False, "error": f"invalid JSON: {e}"})
    if not isinstance(data, dict):
        return _j({"ok": False, "error": "data_json must be a JSON object"})
    return _j(get_backend().topic_pub(topic, msg_type, data, times=times))


@mcp.tool()
def ros2_list_nodes() -> str:
    """List ROS2 nodes."""
    return _j(get_backend().list_nodes())


@mcp.tool()
def ros2_node_info(node: str) -> str:
    """Inspect a node (publishers, subscribers, services).

    Args:
        node: Node name e.g. /turtlesim
    """
    return _j(get_backend().node_info(node))


@mcp.tool()
def ros2_list_services() -> str:
    """List ROS2 services."""
    return _j(get_backend().list_services())


@mcp.tool()
def ros2_service_call(service: str, srv_type: str, request_json: str = "{}") -> str:
    """Call a ROS2 service.

    Args:
        service: Service name e.g. /spawn
        srv_type: Service type e.g. turtlesim/srv/Spawn
        request_json: JSON request body
    """
    try:
        req = json.loads(request_json) if request_json.strip() else {}
    except json.JSONDecodeError as e:
        return _j({"ok": False, "error": f"invalid JSON: {e}"})
    return _j(get_backend().service_call(service, srv_type, req))


@mcp.tool()
def ros2_list_params(node: str | None = None) -> str:
    """List parameters (optional node filter).

    Args:
        node: Optional node name; required in live mode
    """
    return _j(get_backend().list_params(node))


@mcp.tool()
def ros2_get_param(node: str, name: str) -> str:
    """Get a parameter value.

    Args:
        node: Node name
        name: Parameter name
    """
    return _j(get_backend().get_param(node, name))


@mcp.tool()
def ros2_set_param(node: str, name: str, value_json: str) -> str:
    """Set a parameter value (JSON-encoded value).

    Args:
        node: Node name
        name: Parameter name
        value_json: JSON value e.g. 69 or \"hello\" or true
    """
    try:
        value = json.loads(value_json)
    except json.JSONDecodeError:
        value = value_json
    return _j(get_backend().set_param(node, name, value))


@mcp.tool()
def ros2_graph_summary() -> str:
    """Compact graph overview for planning agent actions."""
    return _j(
        {
            "ros2_mcp_version": __version__,
            **get_backend().graph_summary(),
        }
    )


@mcp.tool()
def ros2_tf_tree() -> str:
    """Return TF frame tree (mock: map→odom→base_link; live: /tf echo)."""
    return _j(get_backend().tf_tree())


@mcp.tool()
def ros2_tf_summary() -> str:
    """Summarize mock TF frame count, roots, leaves, and maximum depth."""
    return _j(get_backend().tf_summary())


@mcp.tool()
def ros2_bag_info(path: str | None = None) -> str:
    """Return rosbag metadata.

    Args:
        path: Bag directory or file path. Optional in mock mode, required in live mode.
    """
    return _j(get_backend().bag_info(path))


@mcp.tool()
def ros2_list_actions() -> str:
    """List ROS2 action servers."""
    return _j(get_backend().list_actions())


@mcp.tool()
def ros2_action_send_goal(action: str, action_type: str, goal_json: str = "{}") -> str:
    """Send a goal to a ROS2 action (mock succeeds; live uses ros2 CLI).

    Args:
        action: Action name e.g. /navigate_to_pose
        action_type: Type e.g. nav2_msgs/action/NavigateToPose
        goal_json: JSON goal body
    """
    try:
        goal = json.loads(goal_json) if goal_json.strip() else {}
    except json.JSONDecodeError as e:
        return _j({"ok": False, "error": f"invalid JSON: {e}"})
    return _j(get_backend().action_send_goal(action, action_type, goal))


@mcp.tool()
def lappa_http_bridge(
    base_url: str = "http://127.0.0.1:8840",
    path: str = "/health",
    method: str = "GET",
) -> str:
    """Probe a Lappa IDE server over HTTP (optional bridge for multi-agent ROS workflows).

    Does not require Lappa to be installed in this package. When the server is down,
    returns ok=false with a clear error (safe for mock/CI).

    Args:
        base_url: Lappa server origin (default local IDE)
        path: API path, e.g. /health, /api/demos, /api/sim/state
        method: HTTP method (GET only in this scaffold)
    """
    import urllib.error
    import urllib.request

    method_u = (method or "GET").upper()
    if method_u != "GET":
        return _j({"ok": False, "error": "only GET supported in scaffold", "method": method_u})
    url = base_url.rstrip("/") + "/" + path.lstrip("/")
    try:
        req = urllib.request.Request(url, method="GET", headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=2.0) as resp:  # noqa: S310
            body = resp.read().decode("utf-8", errors="replace")[:4000]
            return _j(
                {
                    "ok": True,
                    "url": url,
                    "status": getattr(resp, "status", 200),
                    "body_preview": body,
                    "bridge": "lappa-http",
                    "ros2_mcp_version": __version__,
                }
            )
    except Exception as exc:  # noqa: BLE001
        return _j(
            {
                "ok": False,
                "url": url,
                "error": str(exc),
                "hint": "Start Lappa with: lappa serve --port 8840",
                "bridge": "lappa-http",
            }
        )


def _instrument_tools() -> int:
    """Wrap every registered MCP tool's fn with the tool-call logger.

    Returns the number of tools instrumented. Idempotent: a tool already
    wrapped (marked via ``_ros2_mcp_logged``) is skipped.
    """
    count = 0
    manager = getattr(mcp, "_tool_manager", None)
    tools = getattr(manager, "_tools", {}) if manager is not None else {}
    for tool in tools.values():
        fn = getattr(tool, "fn", None)
        if fn is None or getattr(fn, "_ros2_mcp_logged", False):
            continue
        wrapped = log_tool_call(fn)
        wrapped._ros2_mcp_logged = True  # type: ignore[attr-defined]
        tool.fn = wrapped
        count += 1
    return count


def run_stdio(verbose: bool = False) -> None:
    """Run the MCP server over stdio.

    Args:
        verbose: When True, enable DEBUG-level structured tool-call logging to
            stderr (stdout stays reserved for the MCP JSON-RPC stream).
    """
    configure_logging(verbose=verbose)
    instrumented = _instrument_tools()
    get_logger().info(
        "serve_start",
        extra={
            "extra_fields": {
                "transport": "stdio",
                "mode": get_mode(),
                "verbose": verbose,
                "tools": instrumented,
                "version": __version__,
            }
        },
    )
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run_stdio()
