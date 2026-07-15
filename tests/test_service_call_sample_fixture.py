"""Service call sample fixture is readable."""
from pathlib import Path


def test_service_call_sample_exists() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "service_call_sample.txt"
    text = p.read_text(encoding="utf-8")
    assert "/add_two_ints" in text
    assert "AddTwoInts" in text
    assert "turtlesim" in text
