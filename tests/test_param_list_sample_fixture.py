"""Param list sample fixture is readable."""
from pathlib import Path


def test_param_list_sample_exists() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "param_list_sample.txt"
    text = p.read_text(encoding="utf-8")
    assert "/talker" in text
    assert "use_sim_time" in text
    assert "/listener" in text
