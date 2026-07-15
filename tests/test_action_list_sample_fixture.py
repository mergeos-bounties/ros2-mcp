"""Action list sample fixture is readable."""
from pathlib import Path


def test_action_list_sample_exists() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "action_list_sample.txt"
    text = p.read_text(encoding="utf-8")
    assert "/fibonacci" in text
    assert "NavigateToPose" in text
    assert "FollowPath" in text
