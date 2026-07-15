"""Node list sample fixture is readable."""
from pathlib import Path


def test_node_list_sample_exists() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "node_list_sample.txt"
    text = p.read_text(encoding="utf-8")
    assert "robot_state_publisher" in text
    assert "amcl" in text
    assert "map_server" in text
