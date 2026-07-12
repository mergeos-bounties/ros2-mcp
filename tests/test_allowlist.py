from ros2_mcp.config import is_pub_allowed, pub_allowlist
from ros2_mcp.backend.live import LiveBackend


def test_allowlist_none_allows_all(monkeypatch):
    monkeypatch.delenv("ROS2_MCP_PUB_ALLOWLIST", raising=False)
    assert pub_allowlist() is None
    assert is_pub_allowed("/anything") is True


def test_allowlist_blocks(monkeypatch):
    monkeypatch.setenv("ROS2_MCP_PUB_ALLOWLIST", "/cmd_vel,/turtle1/cmd_vel")
    assert is_pub_allowed("/cmd_vel") is True
    assert is_pub_allowed("/secret") is False
    live = LiveBackend()
    r = live.topic_pub("/not_allowed", "std_msgs/msg/String", {"data": "x"})
    assert r["ok"] is False
    assert "allowlist" in r
