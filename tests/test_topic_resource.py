import asyncio
import json

from ros2_mcp.config import set_mode
from ros2_mcp.server import mcp, topic_resource


def test_topic_resource_snapshot_mock():
    set_mode("mock")
    out = json.loads(topic_resource("/turtle1/pose"))
    assert out["ok"] is True
    assert out["topic"] == "/turtle1/pose"
    assert out["type"] == "turtlesim/msg/Pose"
    assert out["uri"] == "topic://turtle1/pose"
    assert out["mode"] == "mock"
    assert isinstance(out["messages"], list)
    assert len(out["messages"]) >= 1


def test_topic_resource_normalizes_missing_leading_slash():
    set_mode("mock")
    with_slash = json.loads(topic_resource("/scan"))
    without_slash = json.loads(topic_resource("scan"))
    assert with_slash["topic"] == without_slash["topic"] == "/scan"
    assert with_slash["type"] == without_slash["type"] == "sensor_msgs/msg/LaserScan"


def test_topic_resource_unknown_topic():
    set_mode("mock")
    out = json.loads(topic_resource("/does_not_exist"))
    assert out["ok"] is False
    assert "error" in out


def test_topic_resource_reflects_published_message():
    set_mode("mock")
    from ros2_mcp.server import ros2_topic_pub

    ros2_topic_pub(
        "/turtle1/cmd_vel",
        "geometry_msgs/msg/Twist",
        json.dumps({"linear": {"x": 0.5}, "angular": {"z": 0.2}}),
        1,
    )
    out = json.loads(topic_resource("/turtle1/cmd_vel"))
    assert out["ok"] is True
    assert out["type"] == "geometry_msgs/msg/Twist"
    assert len(out["messages"]) >= 1


def test_topic_resource_registered_as_template():
    # The resource is registered on the FastMCP server as a template
    # (URI contains a parameter), addressable via topic://<name>.
    templates = asyncio.run(mcp.list_resource_templates())
    uris = [t.uriTemplate for t in templates]
    assert "topic://{topic_name}" in uris


def test_topic_resource_read_via_mcp_protocol():
    # Read the resource through the FastMCP read_resource path to prove the
    # topic://<name> URI resolves end-to-end. FastMCP's template matcher binds
    # a single path segment, so a top-level topic name is used here.
    set_mode("mock")
    results = asyncio.run(mcp.read_resource("topic://clock"))
    payload = json.loads(next(iter(results)).content)
    assert payload["ok"] is True
    assert payload["topic"] == "/clock"
    assert payload["type"] == "rosgraph_msgs/msg/Clock"
