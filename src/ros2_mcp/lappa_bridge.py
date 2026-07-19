"""Optional HTTP bridge helpers for Lappa simulator integrations.

The bridge is intentionally mock-safe: if a Lappa HTTP server is not configured
or not reachable, helpers return deterministic local mock data instead of
raising. This keeps MCP tools usable in CI and offline agent sessions.
"""

from __future__ import annotations

import json
import math
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

DEFAULT_LAPPA_BASE_URL = "http://127.0.0.1:8765"
DEFAULT_TIMEOUT_SECONDS = 2.0


def configured_base_url(base_url: str | None = None) -> str:
    """Return a sanitized Lappa base URL from an argument or env var."""
    raw = (base_url or os.environ.get("ROS2_MCP_LAPPA_URL") or DEFAULT_LAPPA_BASE_URL).strip()
    return raw.rstrip("/")


def _mock_pose() -> dict[str, Any]:
    return {
        "frame_id": "map",
        "x": 0.0,
        "y": 0.0,
        "theta": 0.0,
        "linear_velocity": 0.0,
        "angular_velocity": 0.0,
    }


def _normalize_pose(raw: dict[str, Any] | None) -> dict[str, Any]:
    """Normalize common Lappa pose response shapes into stable keys."""
    data: dict[str, Any] = raw or {}
    candidate = data.get("pose")
    pose: dict[str, Any] = candidate if isinstance(candidate, dict) else data
    return {
        "frame_id": str(pose.get("frame_id") or pose.get("frame") or "map"),
        "x": float(pose.get("x", 0.0) or 0.0),
        "y": float(pose.get("y", 0.0) or 0.0),
        "theta": float(pose.get("theta", pose.get("yaw", 0.0)) or 0.0),
    }


def _request_json(method: str, base_url: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    url = urljoin(f"{base_url.rstrip('/')}/", path.lstrip("/"))
    body = json.dumps(payload or {}).encode("utf-8") if payload is not None else None
    request = Request(
        url,
        data=body,
        method=method,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    with urlopen(request, timeout=DEFAULT_TIMEOUT_SECONDS) as response:  # noqa: S310 - user-configured local bridge
        raw = response.read().decode("utf-8")
    if not raw.strip():
        return {}
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        return {"value": parsed}
    return parsed


def _fallback(reason: str, *, base_url: str, cmd_vel: dict[str, Any] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "ok": True,
        "source": "mock",
        "mode": "mock",
        "lappa_available": False,
        "base_url": base_url,
        "reason": reason,
        "pose": _mock_pose(),
    }
    if cmd_vel is not None:
        payload["cmd_vel"] = cmd_vel
    return payload


def lappa_pose(base_url: str | None = None) -> dict[str, Any]:
    """Fetch `/sim/pose` from Lappa, or return a mock pose when unavailable."""
    url = configured_base_url(base_url)
    try:
        raw = _request_json("GET", url, "/sim/pose")
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return _fallback(str(exc), base_url=url)
    return {
        "ok": bool(raw.get("ok", True)),
        "source": "lappa_http",
        "mode": "lappa_http",
        "lappa_available": True,
        "base_url": url,
        "pose": _normalize_pose(raw),
        "raw": raw,
    }


def lappa_cmd_vel(linear_x: float = 0.0, angular_z: float = 0.0, base_url: str | None = None) -> dict[str, Any]:
    """POST a Twist-like cmd_vel to Lappa, falling back to mock-safe output."""
    url = configured_base_url(base_url)
    linear = float(linear_x or 0.0)
    angular = float(angular_z or 0.0)
    cmd_vel = {"linear": {"x": linear}, "angular": {"z": angular}}
    try:
        raw = _request_json("POST", url, "/sim/cmd_vel", cmd_vel)
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        pose = _mock_pose()
        dt = 0.1
        pose["theta"] = angular * dt
        pose["x"] = linear * math.cos(float(pose["theta"])) * dt
        pose["y"] = linear * math.sin(float(pose["theta"])) * dt
        fallback = _fallback(str(exc), base_url=url, cmd_vel=cmd_vel)
        fallback["pose"] = pose
        return fallback
    return {
        "ok": bool(raw.get("ok", True)),
        "source": "lappa_http",
        "mode": "lappa_http",
        "lappa_available": True,
        "base_url": url,
        "cmd_vel": cmd_vel,
        "pose": _normalize_pose(raw),
        "raw": raw,
    }
