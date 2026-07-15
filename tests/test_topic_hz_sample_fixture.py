"""Topic hz sample fixture is readable."""
from pathlib import Path


def test_topic_hz_sample_exists() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "topic_hz_sample.txt"
    text = p.read_text(encoding="utf-8")
    assert "average rate" in text
    assert "/scan" in text
    assert "/odom" in text
