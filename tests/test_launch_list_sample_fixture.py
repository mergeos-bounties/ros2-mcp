"""Launch list sample fixture is readable."""
from pathlib import Path


def test_launch_list_sample_exists() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "launch_list_sample.txt"
    text = p.read_text(encoding="utf-8")
    assert "bringup_launch.py" in text
    assert "turtlebot3" in text
