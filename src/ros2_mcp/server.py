"""FastMCP server: ROS2 tools for AI agents."""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import FastMCP

from ros2_mcp import __version__
from ros2_mcp.backend import get_backend, switch_mode
from ros2_mcp.config import get_mode

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


def run_stdio() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run_stdio()
