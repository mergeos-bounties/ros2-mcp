"""Test CLI --json-file feature for bounty #2."""

import json
import tempfile
from pathlib import Path

from typer.testing import CliRunner

from ros2_mcp.cli import app

runner = CliRunner()


def test_call_with_json_file_topic_pub():
    """Test ros2-mcp call with --json-file for topic_pub."""
    payload = {
        "topic": "/turtle1/cmd_vel",
        "msg_type": "geometry_msgs/msg/Twist",
        "data": {"linear": {"x": 0.5}, "angular": {"z": 0.2}},
        "times": 1,
    }
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(payload, fh)
        json_path = fh.name

    try:
        result = runner.invoke(app, ["call", "topic_pub", "--json-file", json_path])
        assert result.exit_code == 0, f"CLI failed: {result.output}"
        out = result.output.lower()
        assert "ok" in out
        assert "turtle1/cmd_vel" in out
        assert "published" in out
    finally:
        Path(json_path).unlink()


def test_call_with_json_file_service_call():
    """Test ros2-mcp call with --json-file for service_call."""
    payload = {
        "service": "/spawn",
        "srv_type": "turtlesim/srv/Spawn",
        "request": {"name": "turtle42", "x": 1.0, "y": 2.0},
    }
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(payload, fh)
        json_path = fh.name

    try:
        result = runner.invoke(app, ["call", "service_call", "--json-file", json_path])
        assert result.exit_code == 0, f"CLI failed: {result.output}"
        out = result.output.lower()
        assert "ok" in out
        assert "turtle42" in out
    finally:
        Path(json_path).unlink()


def test_call_with_json_file_merge_with_kv_args():
    """Test --json-file merged with inline key=value args (inline overrides)."""
    payload = {"topic": "/turtle1/cmd_vel", "times": 3}
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(payload, fh)
        json_path = fh.name

    try:
        # Inline args override json_file values
        result = runner.invoke(
            app,
            [
                "call",
                "topic_pub",
                "msg_type=geometry_msgs/msg/Twist",
                'data={"linear":{"x":1.0}}',
                "times=1",
                "--json-file",
                json_path,
            ],
        )
        assert result.exit_code == 0, f"CLI failed: {result.output}"
        out = result.output.lower()
        assert "ok" in out
        assert "published" in out
    finally:
        Path(json_path).unlink()


def test_call_topic_hz() -> None:
    """Test ros2-mcp call exposes mock topic_hz parsing."""
    result = runner.invoke(app, ["call", "topic_hz", "topic=/scan"])

    assert result.exit_code == 0, f"CLI failed: {result.output}"
    assert "average_rate_hz" in result.output
    assert "/scan" in result.output


def test_call_with_invalid_json_file():
    """Test error handling for non-existent --json-file."""
    result = runner.invoke(app, ["call", "list_topics", "--json-file", "/nonexistent.json"])
    assert result.exit_code != 0


def test_call_with_json_file_not_object():
    """Test error handling when --json-file contains non-object."""
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(["not", "an", "object"], fh)
        json_path = fh.name

    try:
        result = runner.invoke(app, ["call", "list_topics", "--json-file", json_path])
        assert result.exit_code != 0
        assert "must contain a JSON object" in result.output
    finally:
        Path(json_path).unlink()
