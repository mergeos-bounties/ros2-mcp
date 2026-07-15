"""Interface list sample fixture is readable."""
from pathlib import Path


def test_interface_list_sample_exists() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "interface_list_sample.txt"
    text = p.read_text(encoding="utf-8")
    assert "geometry_msgs" in text
    assert "LaserScan" in text
    assert "NavigateToPose" in text
