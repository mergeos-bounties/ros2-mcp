"""Topic list sample txt fixture is readable."""
from pathlib import Path


def test_topic_list_sample_txt_exists() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "topic_list_sample.txt"
    text = p.read_text(encoding="utf-8")
    assert "/chatter" in text
    assert "/tf" in text
    assert "std_msgs/msg/String" in text
