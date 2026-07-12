from __future__ import annotations

from typing import Any

from ros2_mcp.backend.live import LiveBackend
from ros2_mcp.backend.mock import MockBackend
from ros2_mcp.config import get_mode, set_mode

_mock = MockBackend()
_live = LiveBackend()


def get_backend():
    return _live if get_mode() == "live" else _mock


def switch_mode(mode: str) -> dict[str, Any]:
    m = set_mode(mode)
    backend = get_backend()
    return {"mode": m, "backend": backend.name, "doctor": backend.doctor()}


def mock_instance() -> MockBackend:
    return _mock
