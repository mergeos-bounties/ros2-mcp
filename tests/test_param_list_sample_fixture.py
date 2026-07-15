"""Param list sample fixture is readable."""
from pathlib import Path

from ros2_mcp.backend.parsers import parse_param_list


def test_param_list_sample_exists() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "param_list_sample.txt"
    text = p.read_text(encoding="utf-8")
    assert "robot_description" in text
    assert "use_sim_time" in text


def test_param_list_sample_parses_structured_rows() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "param_list_sample.txt"
    rows = parse_param_list(p.read_text(encoding="utf-8"))
    assert {
        "node": "/robot_state_publisher",
        "name": "robot_description",
        "full_name": "/robot_state_publisher:robot_description",
    } in rows
    assert {
        "node": "/nav2",
        "name": "use_sim_time",
        "full_name": "/nav2:use_sim_time",
    } in rows
