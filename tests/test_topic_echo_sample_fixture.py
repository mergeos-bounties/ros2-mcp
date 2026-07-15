"""Topic echo sample fixture is readable."""
from pathlib import Path


def test_topic_echo_sample_exists() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "topic_echo_sample.txt"
    text = p.read_text(encoding="utf-8")
    assert "/cmd_vel" in text
    assert "geometry_msgs" in text
    assert "/scan" in text
