"""Tests for optional Lappa HTTP bridge tools."""

from __future__ import annotations

import json
import urllib.error
from io import BytesIO
from urllib.request import Request

import pytest
from typer.testing import CliRunner

from ros2_mcp import lappa_bridge
from ros2_mcp.cli import app
from ros2_mcp.server import ros2_lappa_cmd_vel, ros2_lappa_pose


class _Response:
    def __init__(self, body: dict[str, object]) -> None:
        self._body = json.dumps(body).encode()

    def __enter__(self) -> BytesIO:
        return BytesIO(self._body)

    def __exit__(self, *_exc: object) -> None:
        return None


def test_lappa_pose_falls_back_to_mock_when_server_is_down(monkeypatch: pytest.MonkeyPatch) -> None:
    def down(_request: Request, timeout: float = 0.0) -> None:
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr(lappa_bridge, "urlopen", down)

    result = lappa_bridge.lappa_pose(base_url="http://127.0.0.1:9999")

    assert result["ok"] is True
    assert result["source"] == "mock"
    assert result["lappa_available"] is False
    assert result["pose"]["frame_id"] == "map"


def test_lappa_cmd_vel_posts_to_lappa_when_available(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, object] = {}

    def fake_urlopen(request: Request, timeout: float = 0.0) -> _Response:
        seen["url"] = request.full_url
        seen["method"] = request.get_method()
        seen["body"] = json.loads((request.data or b"{}").decode())
        return _Response({"ok": True, "pose": {"x": 1.25, "y": 2.5, "theta": 0.1}})

    monkeypatch.setattr(lappa_bridge, "urlopen", fake_urlopen)

    result = lappa_bridge.lappa_cmd_vel(
        linear_x=0.5,
        angular_z=0.2,
        base_url="http://lappa.local/api",
    )

    assert result["ok"] is True
    assert result["source"] == "lappa_http"
    assert seen["url"] == "http://lappa.local/api/sim/cmd_vel"
    assert seen["method"] == "POST"
    assert seen["body"] == {"linear": {"x": 0.5}, "angular": {"z": 0.2}}
    assert result["pose"] == {"frame_id": "map", "x": 1.25, "y": 2.5, "theta": 0.1}


def test_server_exposes_lappa_tools_with_mock_safe_output(monkeypatch: pytest.MonkeyPatch) -> None:
    def down(_request: Request, timeout: float = 0.0) -> None:
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr(lappa_bridge, "urlopen", down)

    pose = json.loads(ros2_lappa_pose("http://127.0.0.1:9999"))
    cmd = json.loads(ros2_lappa_cmd_vel(0.1, 0.2, "http://127.0.0.1:9999"))

    assert pose["source"] == "mock"
    assert cmd["source"] == "mock"
    assert cmd["cmd_vel"]["linear"]["x"] == 0.1


def test_cli_call_exposes_lappa_cmd_vel_mock_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    def down(_request: Request, timeout: float = 0.0) -> None:
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr(lappa_bridge, "urlopen", down)

    result = CliRunner().invoke(
        app,
        ["call", "lappa_cmd_vel", "linear_x=0.3", "angular_z=0.4", "base_url=http://127.0.0.1:9999"],
    )

    assert result.exit_code == 0, result.output
    assert "mock" in result.output
    assert "cmd_vel" in result.output
