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
