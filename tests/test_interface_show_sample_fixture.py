"""Interface show sample fixture is readable."""
from pathlib import Path


def test_interface_show_sample_exists() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "interface_show_sample.txt"
    text = p.read_text(encoding="utf-8")
    assert "std_msgs/msg/String" in text
    assert "geometry_msgs/msg/Twist" in text
    assert "float64" in text
