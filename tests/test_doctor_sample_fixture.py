"""Smoke: doctor sample fixture is readable."""
from pathlib import Path


def test_doctor_report_sample_exists() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "doctor_report_sample.txt"
    text = p.read_text(encoding="utf-8")
    assert "checks" in text.lower() or "clock" in text.lower()
    assert len(text) > 20
