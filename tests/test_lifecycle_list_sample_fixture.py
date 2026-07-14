"""Lifecycle list sample fixture is readable."""
from pathlib import Path


def test_lifecycle_list_sample_exists() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "lifecycle_list_sample.txt"
    text = p.read_text(encoding="utf-8")
    assert "/map_server" in text
    assert "active" in text
