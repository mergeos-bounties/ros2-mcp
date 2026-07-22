"""FastMCP server: ROS2 tools for AI agents."""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import FastMCP

from ros2_mcp import __version__
from ros2_mcp.backend import get_backend, switch_mode
from ros2_mcp.config import get_mode, is_pub_allowed, pub_allowlist
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
    and must instead be queried via the ``ros2_topic_echo`` tool.
    """
    return _j(get_backend().topic_resource(topic_name))


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
    if not is_pub_allowed(topic):
        allow = pub_allowlist()
        return _j({
            "ok": False,
            "error": (
                f"topic '{topic}' is not in ROS2_MCP_PUB_ALLOWLIST. "
                f"Set env ROS2_MCP_PUB_ALLOWLIST={topic} to allow it."
            ),
            "allowlist": allow,
        })
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
    """Detailed info for a node (publishers, subscribers, services).

    Args:
        node: Fully qualified node name, e.g. /turtlesim
    """
    return _j(get_backend().node_info(node))


@mcp.tool()
def ros2_list_services() -> str:
    """List available ROS2 services."""
    return _j(get_backend().list_services())


@mcp.tool()
def ros2_service_call(
    service: str,
    srv_type: str,
    request_json: str,
) -> str:
    """Call a ROS2 service.

    Args:
        service: Service name e.g. /spawn
        srv_type: Service type e.g. turtlesim/srv/Spawn
        request_json: JSON object body of the request
    """
    try:
        request = json.loads(request_json) if request_json.strip() else {}
    except json.JSONDecodeError as e:
        return _j({"ok": False, "error": f"invalid JSON: {e}"})
    if not isinstance(request, dict):
        return _j({"ok": False, "error": "request_json must be a JSON object"})
    return _j(get_backend().service_call(service, srv_type, request))


@mcp.tool()
def ros2_list_params(node: str | None = None) -> str:
    """List ROS2 parameters for a node.

    Args:
        node: Optional node name. Omit to list all params across all nodes.
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
    """Set a parameter value.

    Args:
        node: Node name
        name: Parameter name
        value_json: JSON-encoded value
    """
    try:
        value = json.loads(value_json) if value_json.strip() else None
    except json.JSONDecodeError as e:
        return _j({"ok": False, "error": f"invalid JSON: {e}"})
    return _j(get_backend().set_param(node, name, value))


@mcp.tool()
def ros2_graph_summary() -> str:
    """Full graph summary: topics, nodes, services, parameters."""
    return _j(get_backend().graph_summary())


@mcp.tool()
def ros2_tf_tree() -> str:
    """Get the TF tree (frame graph)."""
    return _j(get_backend().tf_tree())


@mcp.tool()
def ros2_tf_summary() -> str:
    """Get TF summary: frame count, parent-child relationships, timestamps."""
    return _j(get_backend().tf_summary())


@mcp.tool()
def ros2_bag_info(path: str | None = None) -> str:
    """Get bag file info: topics, duration, message count, storage id.

    Args:
        path: Optional path to bag file. Uses default mock if omitted.
    """
    return _j(get_backend().bag_info(path))


@mcp.tool()
def ros2_list_actions() -> str:
    """List available ROS2 action servers."""
    return _j(get_backend().list_actions())


@mcp.tool()
def ros2_action_send_goal(
    action: str,
    action_type: str,
    goal_json: str,
) -> str:
    """Send a goal to an action server.

    Args:
        action: Action name e.g. /turtle_shape
        action_type: Action type e.g. turtlesim/action/RotateAbsolute
        goal_json: JSON object body of the goal
    """
    try:
        goal = json.loads(goal_json) if goal_json.strip() else {}
    except json.JSONDecodeError as e:
        return _j({"ok": False, "error": f"invalid JSON: {e}"})
    if not isinstance(goal, dict):
        return _j({"ok": False, "error": "goal_json must be a JSON object"})
    return _j(get_backend().action_send_goal(action, action_type, goal))


@mcp.tool()
def ros2_lappa_pose(base_url: str | None = None) -> str:
    """Read robot pose from a Lappa HTTP simulator bridge.

    Args:
        base_url: Lappa base URL (e.g. http://lappa:8080). Uses env LAPPA_BASE_URL if omitted.
    """
    return _j(lappa_pose(base_url))


@mcp.tool()
def ros2_lappa_cmd_vel(
    linear_x: float = 0.0,
    linear_y: float = 0.0,
    angular_z: float = 0.0,
    base_url: str | None = None,
) -> str:
    """Send a velocity command via Lappa HTTP bridge.

    Args:
        linear_x: Linear velocity X
        linear_y: Linear velocity Y
        angular_z: Angular velocity Z
        base_url: Lappa base URL. Uses env LAPPA_BASE_URL if omitted.
    """
    return _j(lappa_cmd_vel(linear_x, linear_y, angular_z, base_url))