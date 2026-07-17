"""Topic bandwidth sample fixture is readable."""
from pathlib import Path


def test_topic_bw_sample_exists() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "topic_bw_sample.txt"
    text = p.read_text(encoding="utf-8")
    assert "/scan" in text
    assert "MB/s" in text
    assert "/camera/image_raw" in text
