from __future__ import annotations

import json

from typer.testing import CliRunner

from ros2_mcp.backend.mock import MockBackend
from ros2_mcp.cli import app
from ros2_mcp.config import set_mode


def test_mock_tf_summary_reports_graph_shape() -> None:
    summary = MockBackend().tf_summary()

    assert summary["ok"] is True
    assert summary["frame_count"] == 5
    assert summary["transform_count"] == 4
    assert summary["roots"] == ["map"]
    assert summary["leaf_frames"] == ["imu_link", "laser_link"]
    assert summary["max_depth"] == 3
    assert "base_link" in summary["frames"]


def test_tf_summary_mcp_tool_returns_json() -> None:
    from ros2_mcp.server import ros2_tf_summary

    set_mode("mock")
    summary = json.loads(ros2_tf_summary())

    assert summary["mode"] == "mock"
    assert summary["frame_count"] == 5


def test_tf_summary_cli_dispatch() -> None:
    result = CliRunner().invoke(app, ["call", "tf_summary"])

    assert result.exit_code == 0
    assert "frame_count" in result.stdout
    assert "laser_link" in result.stdout
