"""Bag info sample fixture is readable."""
from pathlib import Path


def test_bag_info_sample_exists() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "bag_info_sample.txt"
    text = p.read_text(encoding="utf-8")
    assert "/scan" in text
    assert "LaserScan" in text
    assert "duration" in text
