"""TF tree sample fixture is readable."""
from pathlib import Path


def test_tf_tree_sample_exists() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "tf_tree_sample.txt"
    text = p.read_text(encoding="utf-8")
    assert "base_link" in text
    assert "laser_frame" in text
    assert "map" in text
