"""Parsers for `ros2` CLI text output into structured dicts.

These turn the human-oriented text emitted by ``ros2 topic info -v`` and
``ros2 node info <node>`` into JSON-friendly structures so MCP tool callers
don't have to scrape raw text themselves.
"""

from __future__ import annotations

import re
from typing import Any

_COUNT_RE = re.compile(r"^(Publisher|Subscription) count:\s*(\d+)\s*$")
_KV_RE = re.compile(r"^(Node name|Node namespace|Topic type|Endpoint type|GID):\s*(.*)$")
_QOS_KV_RE = re.compile(
    r"^(Reliability|Durability|Lifespan|Deadline|Liveliness|Liveliness lease duration):\s*(.*)$"
)
_TYPE_RE = re.compile(r"^Type:\s*(.*)$")

_NODE_SECTION_RE = re.compile(
    r"^\s*(Subscribers|Publishers|Service Servers|Service Clients|"
    r"Action Servers|Action Clients):\s*$"
)
_NODE_ENTRY_RE = re.compile(r"^\s{2,}(\S+):\s*(.*)$")

_SECTION_KEY_MAP = {
    "Subscribers": "subscribers",
    "Publishers": "publishers",
    "Service Servers": "service_servers",
    "Service Clients": "service_clients",
    "Action Servers": "action_servers",
    "Action Clients": "action_clients",
}


def parse_topic_info_verbose(text: str) -> dict[str, Any]:
    """Parse ``ros2 topic info -v`` (or non-verbose) text output.

    Handles both the verbose form (per-endpoint blocks with QoS profiles) and
    the plain form (``Type:``/``Publisher count:``/``Subscription count:``
    only, no per-endpoint detail).
    """
    result: dict[str, Any] = {
        "type": None,
        "publisher_count": 0,
        "subscription_count": 0,
        "publishers": [],
        "subscribers": [],
    }

    current_endpoint: dict[str, Any] | None = None
    current_list: str | None = None
    in_qos = False

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            continue

        m_type = _TYPE_RE.match(stripped)
        if m_type and current_endpoint is None:
            result["type"] = m_type.group(1).strip()
            continue

        m_count = _COUNT_RE.match(stripped)
        if m_count:
            kind, count = m_count.groups()
            if kind == "Publisher":
                result["publisher_count"] = int(count)
                current_list = "publishers"
            else:
                result["subscription_count"] = int(count)
                current_list = "subscribers"
            current_endpoint = None
            in_qos = False
            continue

        if stripped == "QoS profile:":
            in_qos = True
            continue

        m_kv = _KV_RE.match(stripped)
        if m_kv and current_list is not None:
            key, value = m_kv.groups()
            if key == "Node name":
                current_endpoint = {
                    "node_name": value.strip(),
                    "node_namespace": "",
                    "topic_type": result["type"],
                    "endpoint_type": "",
                    "gid": "",
                    "qos": {},
                }
                result[current_list].append(current_endpoint)
                in_qos = False
                continue
            if current_endpoint is not None:
                field = {
                    "Node namespace": "node_namespace",
                    "Topic type": "topic_type",
                    "Endpoint type": "endpoint_type",
                    "GID": "gid",
                }[key]
                current_endpoint[field] = value.strip()
                in_qos = False
                continue

        m_qos = _QOS_KV_RE.match(stripped)
        if m_qos and in_qos and current_endpoint is not None:
            key, value = m_qos.groups()
            qos_key = key.lower().replace(" ", "_")
            current_endpoint["qos"][qos_key] = value.strip()
            continue

    return result


def parse_node_info(text: str) -> dict[str, Any]:
    """Parse ``ros2 node info <node>`` text output.

    Returns a dict with a section per endpoint kind, each a list of
    ``{"name": ..., "type": ...}`` entries. The leading line (node name) is
    skipped; callers already know the node name they asked for.
    """
    result: dict[str, list[dict[str, str]]] = {
        "subscribers": [],
        "publishers": [],
        "service_servers": [],
        "service_clients": [],
        "action_servers": [],
        "action_clients": [],
    }

    current_key: str | None = None
    for raw_line in text.splitlines():
        if not raw_line.strip():
            continue
        m_section = _NODE_SECTION_RE.match(raw_line)
        if m_section:
            current_key = _SECTION_KEY_MAP[m_section.group(1)]
            continue
        m_entry = _NODE_ENTRY_RE.match(raw_line)
        if m_entry and current_key is not None:
            name, typ = m_entry.groups()
            result[current_key].append({"name": name.strip(), "type": typ.strip()})

    return result
