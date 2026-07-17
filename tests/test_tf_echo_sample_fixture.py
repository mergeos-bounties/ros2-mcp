"""TF echo sample fixture is readable."""
from pathlib import Path


def test_tf_echo_sample_exists() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "tf_echo_sample.txt"
    text = p.read_text(encoding="utf-8")
    assert "Translation" in text
    assert "Quaternion" in text
    assert "0.120" in text
