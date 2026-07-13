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


def parse_action_list(raw: str) -> list[dict[str, str]]:
    """Parse ``ros2 action list -t`` lines like ``/fibonacci [example_interfaces/action/Fibonacci]``."""
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


def parse_param_list(raw: str) -> list[str]:
    """Parse ``ros2 param list`` plain text into fully-qualified parameter names."""
    params: list[str] = []
    for line in (raw or "").splitlines():
        name = line.strip()
        if not name or name.startswith("#"):
            continue
        params.append(name)
    return params


def parse_interface_list(raw: str) -> list[str]:
    """Parse ``ros2 interface list`` plain text into interface type names."""
    items: list[str] = []
    for line in (raw or "").splitlines():
        name = line.strip()
        if not name or name.startswith("#") or name.endswith(":"):
            continue
        # Skip section headers like "Messages:" / "Services:"
        if name.lower() in {"messages", "services", "actions"}:
            continue
        items.append(name)
    return items


def parse_pkg_list(raw: str) -> list[str]:
    """Parse ``ros2 pkg list`` plain text into package names."""
    pkgs: list[str] = []
    for line in (raw or "").splitlines():
        name = line.strip()
        if not name or name.startswith("#"):
            continue
        pkgs.append(name)
    return pkgs


def parse_topic_list(raw: str) -> list[dict[str, str]]:
    """Parse ``ros2 topic list -t`` lines like ``/chatter [std_msgs/msg/String]``."""
    items: list[dict[str, str]] = []
    for line in (raw or "").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "[" in line and line.endswith("]"):
            name, typ = line.rsplit("[", 1)
            items.append({"name": name.strip(), "type": typ[:-1].strip()})
        else:
            items.append({"name": line, "type": ""})
    return items


def parse_tf_frames(raw: str) -> list[str]:
    """Parse loose ``tf2_echo`` / frame dump lines into frame ids (best-effort)."""
    frames: list[str] = []
    seen: set[str] = set()
    for line in (raw or "").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Common patterns: "Frame: base_link" or bare frame names
        if line.lower().startswith("frame:"):
            name = line.split(":", 1)[1].strip()
        else:
            name = line.split()[0]
        if name and name not in seen and not name.startswith("["):
            seen.add(name)
            frames.append(name)
    return frames


def parse_bag_info(raw: str) -> dict[str, object]:
    """Parse a subset of ``ros2 bag info`` text into key fields (best-effort)."""
    out: dict[str, object] = {"ok": True, "path": None, "duration": None, "messages": None, "topics": []}
    for line in (raw or "").splitlines():
        s = line.strip()
        if s.lower().startswith("files:"):
            out["path"] = s.split(":", 1)[1].strip()
        elif s.lower().startswith("duration:"):
            out["duration"] = s.split(":", 1)[1].strip()
        elif s.lower().startswith("messages:"):
            try:
                out["messages"] = int(s.split(":", 1)[1].strip().split()[0])
            except Exception:
                out["messages"] = s.split(":", 1)[1].strip()
        elif s.startswith("Topic:") or s.startswith("/"):
            # "Topic: /chatter | Type: std_msgs/msg/String | Count: 10"
            name = s
            if "|" in s:
                name = s.split("|", 1)[0]
            name = name.replace("Topic:", "").strip()
            if name.startswith("/"):
                topics = out["topics"]
                if isinstance(topics, list):
                    topics.append(name)
    return out


def parse_doctor_report(raw: str) -> dict[str, object]:
    """Parse a loose subset of ``ros2 doctor`` / health text into summary fields."""
    text = raw or ""
    out: dict[str, object] = {
        "ok": True,
        "warnings": 0,
        "errors": 0,
        "lines": [],
    }
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    out["lines"] = lines[:50]
    warn = sum(1 for ln in lines if "warn" in ln.lower())
    err = sum(1 for ln in lines if "error" in ln.lower() or "fail" in ln.lower())
    out["warnings"] = warn
    out["errors"] = err
    out["ok"] = err == 0
    return out


def parse_launch_list(raw: str) -> list[dict[str, str]]:
    """Parse loose ``ros2 launch`` package listing lines into name/path pairs."""
    items: list[dict[str, str]] = []
    for line in (raw or "").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if " " in line:
            name, path = line.split(None, 1)
            items.append({"name": name, "path": path})
        else:
            items.append({"name": line, "path": ""})
    return items
