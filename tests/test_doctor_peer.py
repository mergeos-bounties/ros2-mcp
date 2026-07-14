"""Doctor mock exposes peer_count."""
from ros2_mcp.backend.mock import MockBackend


def test_doctor_peer_count() -> None:
    d = MockBackend().doctor()
    assert d.get("ok") is True
    assert "peer_count" in d
    assert isinstance(d["peer_count"], int)
