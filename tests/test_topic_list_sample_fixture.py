"""Topic list sample fixture is readable."""
from pathlib import Path


def test_topic_list_sample_exists() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "topic_list_sample.txt"
    text = p.read_text(encoding="utf-8")
    assert "/chatter" in text
    assert "std_msgs" in text
