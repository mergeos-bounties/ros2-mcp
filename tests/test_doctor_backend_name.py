from ros2_mcp.backend.mock import MockBackend

def test_doctor_backend_name() -> None:
    d = MockBackend().doctor()
    assert d.get("ok") is True
    assert d.get("backend_name") == "mock"
