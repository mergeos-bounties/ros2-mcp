"""Node info sample fixture is readable."""
from pathlib import Path

from ros2_mcp.backend.live import LiveBackend
from ros2_mcp.backend.parsers import parse_node_info


def test_node_info_sample_parses_sections() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "node_info_sample.txt"
    text = p.read_text(encoding="utf-8")
    assert "/talker" in text
    assert "Publishers:" in text
    assert "/chatter" in text

    info = parse_node_info(text)
    assert info["ok"] is True
    assert info["name"] == "/talker"
    assert info["publishers"] == [
        {"name": "/chatter", "type": "std_msgs/msg/String"},
        {"name": "/rosout", "type": "rcl_interfaces/msg/Log"},
    ]
    assert info["subscribers"] == [
        {"name": "/parameter_events", "type": "rcl_interfaces/msg/ParameterEvent"}
    ]
    assert info["service_servers"] == [
        {"name": "/talker/describe_parameters", "type": "rcl_interfaces/srv/DescribeParameters"}
    ]
    assert info["service_clients"] == []
    assert info["action_servers"] == []
    assert info["action_clients"] == []


def test_node_info_parser_uses_safe_defaults() -> None:
    info = parse_node_info("", node="/fallback")
    assert info["ok"] is True
    assert info["name"] == "/fallback"
    assert info["publishers"] == []
    assert info["subscribers"] == []
    assert info["service_servers"] == []
    assert info["service_clients"] == []
    assert info["action_servers"] == []
    assert info["action_clients"] == []


def test_live_node_info_uses_structured_parser() -> None:
    raw = (Path(__file__).resolve().parents[1] / "examples" / "node_info_sample.txt").read_text(
        encoding="utf-8"
    )
    backend = LiveBackend()
    backend._run = lambda args: (0, raw, "")  # type: ignore[method-assign]

    info = backend.node_info("/talker")

    assert info["ok"] is True
    assert info["parsed"] is True
    assert info["name"] == "/talker"
    assert info["publishers"][0]["name"] == "/chatter"
