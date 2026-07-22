"""Mock TF tree tool returning map -> odom -> base_link."""

from __future__ import annotations

from typing import Any


def mock_tf_tree() -> dict[str, Any]:
    """Return a mock TF tree with map -> odom -> base_link chain.

    Returns a dictionary with frame metadata and the full parent chain
    suitable for offline development and testing.
    """
    frames = {
        "map": {
            "parent": None,
            "translation": [0.0, 0.0, 0.0],
            "rotation": [0.0, 0.0, 0.0, 1.0],
            "children": ["odom"],
        },
        "odom": {
            "parent": "map",
            "translation": [1.5, 0.0, 0.0],
            "rotation": [0.0, 0.0, 0.0, 1.0],
            "children": ["base_link"],
        },
        "base_link": {
            "parent": "odom",
            "translation": [0.0, 0.0, 0.5],
            "rotation": [0.0, 0.0, 0.0, 1.0],
            "children": [],
        },
    }
    return {
        "ok": True,
        "tree": "map -> odom -> base_link",
        "frames": frames,
        "frame_count": len(frames),
    }
