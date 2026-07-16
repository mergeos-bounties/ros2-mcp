"""Topic hz sample fixture is readable."""
from pathlib import Path

from ros2_mcp.backend.parsers import parse_topic_hz


def test_topic_hz_sample_exists() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "topic_hz_sample.txt"
    text = p.read_text(encoding="utf-8")
    assert "average rate" in text
    assert "/scan" in text
    assert "/odom" in text


def test_parse_topic_hz_sample_fixture() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "topic_hz_sample.txt"
    info = parse_topic_hz(p.read_text(encoding="utf-8"))

    assert info["ok"] is True
    assert info["topic_count"] == 2
    assert info["topics"] == [
        {
            "topic": "/scan",
            "average_rate_hz": 10.012,
            "min_s": 0.098,
            "max_s": 0.105,
            "std_dev_s": 0.002,
            "window": 50,
        },
        {
            "topic": "/odom",
            "average_rate_hz": 15.004,
            "min_s": 0.065,
            "max_s": 0.068,
            "std_dev_s": 0.001,
            "window": 80,
        },
    ]
