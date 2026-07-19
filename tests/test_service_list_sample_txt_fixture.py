"""Service list sample txt fixture is readable."""
from pathlib import Path


def test_service_list_sample_txt_exists() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "service_list_sample.txt"
    text = p.read_text(encoding="utf-8")
    assert "Services:" in text
    assert "/spawn" in text
    assert "turtlesim" in text
    assert "/clear" in text
