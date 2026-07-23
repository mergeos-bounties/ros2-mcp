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


def _read_allowlist_file(file_path: str) -> list[str] | None:
    if not file_path or not os.path.isfile(file_path):
        return None
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        items = []
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                items.extend([p.strip() for p in line.split(",") if p.strip()])
        return items if items else None
    except OSError:
        return None


def pub_allowlist() -> list[str] | None:
    """Optional publish allowlist for mock and live modes.

    Env ``ROS2_MCP_PUB_ALLOWLIST=/cmd_vel,/turtle1/cmd_vel`` (comma-separated).
    Or env ``ROS2_MCP_PUB_ALLOWLIST_FILE=/path/to/allowlist.txt`` (one item per line or comma-separated).
    Empty / unset → all topics allowed.
    """
    file_path = (os.environ.get("ROS2_MCP_PUB_ALLOWLIST_FILE") or "").strip()
    from_file = _read_allowlist_file(file_path)
    if from_file is not None:
        return from_file

    raw = (os.environ.get("ROS2_MCP_PUB_ALLOWLIST") or "").strip()
    if not raw:
        return None
    return [p.strip() for p in raw.split(",") if p.strip()]


def service_allowlist() -> list[str] | None:
    """Optional service-call allowlist for mock and live modes.

    Env ``ROS2_MCP_SERVICE_ALLOWLIST=/spawn,/clear`` (comma-separated).
    Or env ``ROS2_MCP_SERVICE_ALLOWLIST_FILE=/path/to/allowlist.txt`` (one item per line or comma-separated).
    Empty / unset → all services allowed.
    """
    file_path = (os.environ.get("ROS2_MCP_SERVICE_ALLOWLIST_FILE") or "").strip()
    from_file = _read_allowlist_file(file_path)
    if from_file is not None:
        return from_file

    raw = (os.environ.get("ROS2_MCP_SERVICE_ALLOWLIST") or "").strip()
    if not raw:
        return None
    return [p.strip() for p in raw.split(",") if p.strip()]


def _matches_name_allowlist(name: str, allow: list[str]) -> bool:
    candidate = name.strip()
    allowed = {item.strip() for item in allow if item.strip()}
    if not candidate:
        return False
    variants = {candidate}
    if candidate.startswith("/"):
        variants.add(candidate.lstrip("/"))
    else:
        variants.add(f"/{candidate}")
    return bool(variants & allowed)


def is_pub_allowed(topic: str) -> bool:
    allow = pub_allowlist()
    if allow is None:
        return True
    return _matches_name_allowlist(topic, allow)


def is_service_allowed(service: str) -> bool:
    allow = service_allowlist()
    if allow is None:
        return True
    return _matches_name_allowlist(service, allow)
