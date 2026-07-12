"""Structured parsers for ros2 CLI text output."""

from __future__ import annotations

import re
from typing import Any


def parse_topic_info_verbose(raw: str, topic: str = "") -> dict[str, Any]:
    """
    Parse `ros2 topic info <topic> -v` into structured fields.

    Works with common Rolling/Humble layouts; falls back to raw on failure.
    """
    text = raw or ""
    out: dict[str, Any] = {
        "ok": True,
        "name": topic or None,
        "type": None,
        "publisher_count": None,
        "subscription_count": None,
        "publishers": [],
        "subscriptions": [],
        "raw": text,
    }

    # Type: std_msgs/msg/String
    m = re.search(r"Type:\s*(\S+)", text, flags=re.I)
    if m:
        out["type"] = m.group(1)

    m = re.search(r"Publisher count:\s*(\d+)", text, flags=re.I)
    if m:
        out["publisher_count"] = int(m.group(1))
    m = re.search(r"Subscription count:\s*(\d+)", text, flags=re.I)
    if m:
        out["subscription_count"] = int(m.group(1))

    # Endpoint blocks may list Node name before or after Endpoint type.
    current: dict[str, Any] | None = None
    pending_node: str | None = None
    for line in text.splitlines():
        line_s = line.strip()
        nm = re.match(r"Node name:\s*(\S+)", line_s, flags=re.I)
        if nm:
            pending_node = nm.group(1)
            if current is not None and "node" not in current:
                current["node"] = pending_node
            continue
        if re.match(r"Endpoint type:\s*PUBLISHER", line_s, flags=re.I):
            current = {}
            if pending_node:
                current["node"] = pending_node
                pending_node = None
            out["publishers"].append(current)
            continue
        if re.match(r"Endpoint type:\s*SUBSCRIPTION", line_s, flags=re.I):
            current = {}
            if pending_node:
                current["node"] = pending_node
                pending_node = None
            out["subscriptions"].append(current)
            continue
        if current is not None:
            ni = re.match(r"Node namespace:\s*(\S+)", line_s, flags=re.I)
            if ni:
                current["namespace"] = ni.group(1)
            tq = re.match(r"Topic type:\s*(\S+)", line_s, flags=re.I)
            if tq:
                current["type"] = tq.group(1)
            if re.match(r"QoS profile:", line_s, flags=re.I):
                current["qos"] = True

    if out["publisher_count"] is None:
        out["publisher_count"] = len(out["publishers"])
    if out["subscription_count"] is None:
        out["subscription_count"] = len(out["subscriptions"])

    # Topic name line sometimes first
    if not out["name"]:
        m = re.search(r"Topic:\s*(\S+)", text, flags=re.I)
        if m:
            out["name"] = m.group(1)

    return out


def parse_node_list(raw: str) -> list[str]:
    """Parse ``ros2 node list`` plain text into node name list."""
    nodes: list[str] = []
    for line in (raw or "").splitlines():
        name = line.strip()
        if not name or name.startswith("#"):
            continue
        if not name.startswith("/"):
            name = "/" + name
        nodes.append(name)
    return nodes


def parse_service_list(raw: str) -> list[dict[str, str]]:
    """Parse ``ros2 service list -t`` lines like ``/foo [std_srvs/srv/Empty]``."""
    items: list[dict[str, str]] = []
    for line in (raw or "").splitlines():
        line = line.strip()
        if not line:
            continue
        if "[" in line and line.endswith("]"):
            name, typ = line.rsplit("[", 1)
            items.append({"name": name.strip(), "type": typ[:-1].strip()})
        else:
            items.append({"name": line, "type": ""})
    return items
