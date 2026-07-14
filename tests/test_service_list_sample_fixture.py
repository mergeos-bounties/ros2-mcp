"""Service list sample fixture is readable."""
from pathlib import Path


def test_service_list_sample_exists() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "service_list_sample.txt"
    text = p.read_text(encoding="utf-8")
    assert "/add_two_ints" in text
    assert "/spawn_entity" in text
