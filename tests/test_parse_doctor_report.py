from ros2_mcp.backend.parsers import parse_doctor_report


def test_parse_doctor_report_ok():
    raw = """
All checks passed
Network: ok
DDS: default
"""
    out = parse_doctor_report(raw)
    assert out["ok"] is True
    assert out["errors"] == 0
    assert out["warnings"] == 0
    assert len(out["lines"]) >= 2


def test_parse_doctor_report_warn_and_error():
    raw = """
WARN: QoS mismatch on /scan
ERROR: RMW plugin failed to load
fail: cannot contact daemon
info: continuing
"""
    out = parse_doctor_report(raw)
    assert out["ok"] is False
    assert out["errors"] >= 2
    assert out["warnings"] >= 1
    assert any("QoS" in ln or "qos" in ln.lower() for ln in out["lines"])


def test_parse_doctor_report_empty():
    out = parse_doctor_report("")
    assert out["ok"] is True
    assert out["lines"] == []
    assert out["warnings"] == 0
    assert out["errors"] == 0
