"""Action goal sample fixture is readable."""
from pathlib import Path


def test_action_goal_sample_exists() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "action_goal_sample.txt"
    text = p.read_text(encoding="utf-8")
    assert "target_pose" in text
    assert "SUCCEEDED" in text
