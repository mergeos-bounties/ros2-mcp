"""Diagnostics echo sample fixture is readable."""
from pathlib import Path


def test_diagnostics_echo_sample_exists() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "diagnostics_echo_sample.txt"
    text = p.read_text(encoding="utf-8")
    assert "/diagnostics" in text
    assert "battery" in text
    assert "cpu" in text
