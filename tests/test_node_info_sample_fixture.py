"""Node info sample fixture is readable."""
from pathlib import Path


def test_node_info_sample_exists() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "node_info_sample.txt"
    text = p.read_text(encoding="utf-8")
    assert "/talker" in text
    assert "Publishers:" in text
    assert "/chatter" in text
