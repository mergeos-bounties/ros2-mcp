from ros2_mcp.backend.mock import MockBackend


def test_doctor_includes_sim_time():
    b = MockBackend()
    d = b.doctor()
    assert d["ok"] is True
    assert "sim_time_sec" in d
    assert d["sim_time_sec"] >= 0
    assert d.get("clock_source") == "mock_steady"
    assert d.get("namespace_count", 0) >= 1
    assert d.get("topic_type_count", 0) >= 1
