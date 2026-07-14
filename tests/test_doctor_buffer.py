"""Doctor mock exposes buffer stats."""
from ros2_mcp.backend.mock import MockBackend


def test_doctor_buffered_fields() -> None:
    b = MockBackend()
    d = b.doctor()
    assert d.get("ok") is True
    assert "buffered_messages" in d
    assert "buffer_topics" in d
    assert isinstance(d["buffered_messages"], int)
    assert isinstance(d["buffer_topics"], int)
