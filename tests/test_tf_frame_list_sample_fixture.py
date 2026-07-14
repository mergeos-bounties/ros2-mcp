"""TF frame list sample fixture is readable."""
from pathlib import Path


def test_tf_frame_list_sample_exists() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "tf_frame_list_sample.txt"
    text = p.read_text(encoding="utf-8")
    assert "map" in text
    assert "base_link" in text
