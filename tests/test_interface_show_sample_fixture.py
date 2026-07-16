"""Interface show sample fixture is readable."""
from pathlib import Path

from ros2_mcp.backend.parsers import parse_interface_show


def test_interface_show_sample_exists() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "interface_show_sample.txt"
    text = p.read_text(encoding="utf-8")
    assert "std_msgs/msg/String" in text
    assert "geometry_msgs/msg/Twist" in text
    assert "float64" in text


def test_interface_show_sample_parses_nested_fields() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "interface_show_sample.txt"
    blocks = [block for block in p.read_text(encoding="utf-8").split("\n\n") if block.strip()]

    parsed = [parse_interface_show(block) for block in blocks]

    twist = next(item for item in parsed if item["type"] == "geometry_msgs/msg/Twist")
    fields = twist["fields"]
    assert isinstance(fields, list)
    assert {"type": "float64", "name": "x", "path": "linear.x", "indent": 8} in fields
    assert {"type": "float64", "name": "z", "path": "angular.z", "indent": 8} in fields
