from ros2_mcp.config import is_pub_allowed, is_service_allowed, pub_allowlist, service_allowlist
from ros2_mcp.backend.live import LiveBackend
from ros2_mcp.backend.mock import MockBackend


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


def test_service_allowlist_none_allows_all(monkeypatch):
    monkeypatch.delenv("ROS2_MCP_SERVICE_ALLOWLIST", raising=False)
    assert service_allowlist() is None
    assert is_service_allowed("/spawn") is True


def test_service_allowlist_blocks_mock(monkeypatch):
    monkeypatch.setenv("ROS2_MCP_SERVICE_ALLOWLIST", "/spawn,/clear")
    assert service_allowlist() == ["/spawn", "/clear"]
    assert is_service_allowed("spawn") is True
    assert is_service_allowed("/kill") is False

    mock = MockBackend()
    blocked = mock.service_call("/kill", "turtlesim/srv/Kill", {"name": "turtle1"})
    assert blocked["ok"] is False
    assert "ROS2_MCP_SERVICE_ALLOWLIST" in blocked["error"]
    assert blocked["allowlist"] == ["/spawn", "/clear"]

    allowed = mock.service_call("/spawn", "turtlesim/srv/Spawn", {"name": "safe"})
    assert allowed["ok"] is True


def test_service_allowlist_blocks_live_before_ros2_call(monkeypatch):
    monkeypatch.setenv("ROS2_MCP_SERVICE_ALLOWLIST", "/spawn")
    live = LiveBackend()
    blocked = live.service_call("/kill", "turtlesim/srv/Kill", {"name": "turtle1"})
    assert blocked["ok"] is False
    assert "ROS2_MCP_SERVICE_ALLOWLIST" in blocked["error"]
    assert blocked["allowlist"] == ["/spawn"]


def test_pub_allowlist_blocks_mock(monkeypatch):
    monkeypatch.setenv("ROS2_MCP_PUB_ALLOWLIST", "/cmd_vel,/turtle1/cmd_vel")
    mock = MockBackend()
    blocked = mock.topic_pub("/not_allowed", "std_msgs/msg/String", {"data": "x"})
    assert blocked["ok"] is False
    assert "ROS2_MCP_PUB_ALLOWLIST" in blocked["error"]
    assert blocked["allowlist"] == ["/cmd_vel", "/turtle1/cmd_vel"]

    allowed = mock.topic_pub("/cmd_vel", "geometry_msgs/msg/Twist", {"linear": {"x": 1.0}})
    assert allowed.get("ok") is not False


def test_pub_allowlist_file(monkeypatch, tmp_path):
    f = tmp_path / "allowlist.txt"
    f.write_text("# Comments ignored\n/cmd_vel\n/turtle1/cmd_vel, /chatter\n")
    monkeypatch.setenv("ROS2_MCP_PUB_ALLOWLIST_FILE", str(f))
    assert pub_allowlist() == ["/cmd_vel", "/turtle1/cmd_vel", "/chatter"]
    assert is_pub_allowed("/chatter") is True
    assert is_pub_allowed("/forbidden") is False


def test_service_allowlist_file(monkeypatch, tmp_path):
    f = tmp_path / "services.txt"
    f.write_text("/spawn\n/clear\n")
    monkeypatch.setenv("ROS2_MCP_SERVICE_ALLOWLIST_FILE", str(f))
    assert service_allowlist() == ["/spawn", "/clear"]
    assert is_service_allowed("/spawn") is True
    assert is_service_allowed("/reset") is False

