from ros2_mcp.backend.mock import MockBackend


def test_doctor_includes_sim_time():
    b = MockBackend()
    d = b.doctor()
    assert d["ok"] is True
    assert "sim_time_sec" in d
    assert d["sim_time_sec"] >= 0
    assert d.get("clock_source") == "mock_steady"
