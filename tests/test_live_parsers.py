"""Tests for structured parsing of `ros2 topic info -v` / `ros2 node info`.

Uses captured CLI-output fixtures (no live ROS2 install needed) and a
monkeypatched LiveBackend._run to exercise the backend end-to-end.
"""

from __future__ import annotations

from pathlib import Path

from ros2_mcp.backend.live import LiveBackend
from ros2_mcp.backend.parsers import parse_node_info, parse_topic_info_verbose

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> str:
    return (FIXTURES / name).read_text()


def test_parse_topic_info_verbose_fields():
    parsed = parse_topic_info_verbose(_load("topic_info_verbose.txt"))
    assert parsed["type"] == "geometry_msgs/msg/Twist"
    assert parsed["publisher_count"] == 1
    assert parsed["subscription_count"] == 2
    assert len(parsed["publishers"]) == 1
    assert len(parsed["subscribers"]) == 2

    pub = parsed["publishers"][0]
    assert pub["node_name"] == "teleop_turtle"
    assert pub["node_namespace"] == "/"
    assert pub["endpoint_type"] == "PUBLISHER"
    assert pub["topic_type"] == "geometry_msgs/msg/Twist"
    assert pub["gid"].startswith("01.0f.b3.4a")
    assert pub["qos"]["reliability"] == "RELIABLE"
    assert pub["qos"]["durability"] == "VOLATILE"
    assert pub["qos"]["liveliness"] == "AUTOMATIC"

    sub_names = {s["node_name"] for s in parsed["subscribers"]}
    assert sub_names == {"turtlesim", "recorder"}
    recorder = next(s for s in parsed["subscribers"] if s["node_name"] == "recorder")
    assert recorder["qos"]["reliability"] == "BEST_EFFORT"


def test_parse_topic_info_plain():
    parsed = parse_topic_info_verbose(_load("topic_info_plain.txt"))
    assert parsed["type"] == "sensor_msgs/msg/LaserScan"
    assert parsed["publisher_count"] == 1
    assert parsed["subscription_count"] == 0
    assert parsed["publishers"] == []
    assert parsed["subscribers"] == []


def test_parse_node_info_sections():
    parsed = parse_node_info(_load("node_info.txt"))
    assert {"name": "/turtle1/cmd_vel", "type": "geometry_msgs/msg/Twist"} in parsed["subscribers"]
    assert len(parsed["subscribers"]) == 2
    assert len(parsed["publishers"]) == 4
    assert {"name": "/spawn", "type": "turtlesim/srv/Spawn"} in parsed["service_servers"]
    assert len(parsed["service_servers"]) == 5
    assert parsed["service_clients"] == []
    assert parsed["action_servers"] == [
        {"name": "/turtle1/rotate_absolute", "type": "turtlesim/action/RotateAbsolute"}
    ]
    assert parsed["action_clients"] == []


def test_live_topic_info_structured(monkeypatch):
    text = _load("topic_info_verbose.txt")
    b = LiveBackend()
    monkeypatch.setattr(b, "_run", lambda args, timeout=15.0: (0, text, ""))
    info = b.topic_info("/turtle1/cmd_vel")
    assert info["ok"] is True
    assert info["name"] == "/turtle1/cmd_vel"
    assert info["type"] == "geometry_msgs/msg/Twist"
    assert info["publisher_count"] == 1
    assert info["subscription_count"] == 2
    assert info["raw"] == text  # raw preserved for backward compat


def test_live_topic_info_falls_back_to_plain(monkeypatch):
    plain = _load("topic_info_plain.txt")

    def fake_run(args, timeout=15.0):
        if "-v" in args:
            return 1, "", "verbose not supported"
        return 0, plain, ""

    b = LiveBackend()
    monkeypatch.setattr(b, "_run", fake_run)
    info = b.topic_info("/scan")
    assert info["ok"] is True
    assert info["type"] == "sensor_msgs/msg/LaserScan"
    assert info["publisher_count"] == 1


def test_live_node_info_structured(monkeypatch):
    text = _load("node_info.txt")
    b = LiveBackend()
    monkeypatch.setattr(b, "_run", lambda args, timeout=15.0: (0, text, ""))
    info = b.node_info("/turtlesim")
    assert info["ok"] is True
    assert info["name"] == "/turtlesim"
    assert len(info["publishers"]) == 4
    assert len(info["service_servers"]) == 5
    assert info["raw"] == text


def test_live_topic_info_error(monkeypatch):
    b = LiveBackend()
    monkeypatch.setattr(b, "_run", lambda args, timeout=15.0: (1, "", "topic not found"))
    info = b.topic_info("/nope")
    assert info["ok"] is False
    assert "topic not found" in info["error"]
