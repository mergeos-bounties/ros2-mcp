from __future__ import annotations

import os
from typing import Literal

Mode = Literal["mock", "live"]


def get_mode() -> Mode:
    raw = (os.environ.get("ROS2_MCP_MODE") or "mock").strip().lower()
    return "live" if raw == "live" else "mock"


def set_mode(mode: str) -> Mode:
    m: Mode = "live" if mode.strip().lower() == "live" else "mock"
    os.environ["ROS2_MCP_MODE"] = m
    return m


def ros2_bin() -> str:
    return os.environ.get("ROS2_MCP_ROS2_BIN") or "ros2"


def domain_id() -> str:
    return os.environ.get("ROS2_MCP_DOMAIN_ID") or os.environ.get("ROS_DOMAIN_ID") or "0"


def pub_allowlist() -> list[str] | None:
    """Optional live-mode publish allowlist.

    Env ``ROS2_MCP_PUB_ALLOWLIST=/cmd_vel,/turtle1/cmd_vel`` (comma-separated).
    Empty / unset → all topics allowed.
    """
    raw = (os.environ.get("ROS2_MCP_PUB_ALLOWLIST") or "").strip()
    if not raw:
        return None
    return [p.strip() for p in raw.split(",") if p.strip()]


def is_pub_allowed(topic: str) -> bool:
    allow = pub_allowlist()
    if allow is None:
        return True
    t = topic.strip()
    return t in allow or (t.startswith("/") and t in allow)


from pathlib import Path as _Path
ALLOWLIST_PATH = _Path(os.environ.get("ROS2_MCP_DATA_DIR", _Path.home() / ".ros2_mcp")) / "allowlist.json"
