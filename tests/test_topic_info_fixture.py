"""Golden fixture for verbose topic info parsing."""
from __future__ import annotations

import json
from pathlib import Path

from ros2_mcp.backend.parsers import parse_topic_info_verbose


def test_topic_info_verbose_fixture() -> None:
    raw = (Path(__file__).resolve().parents[1] / "examples" / "topic_info_verbose.txt").read_text(
        encoding="utf-8"
    )
    info = parse_topic_info_verbose(raw)
    assert info is not None
    if isinstance(info, dict):
        blob = json.dumps(info).lower()
    else:
        blob = (str(info) + json.dumps(getattr(info, "__dict__", {}), default=str)).lower()
    assert any(
        tok in blob for tok in ("string", "std_msgs", "publisher", "subscription", "reliable")
    )
