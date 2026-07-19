"""Tests for the demo command and tool inventory table."""

import pytest
from typer.testing import CliRunner

from ros2_mcp.cli import app


@pytest.fixture
def runner():
    return CliRunner()


def test_demo_command(runner):
    """Test that demo command runs and includes tool inventory table."""
    result = runner.invoke(app, ["demo"])
    assert result.exit_code == 0
    assert "ros2-mcp Tool Inventory" in result.output
    assert "ros2_mode" in result.output
    assert "ros2_doctor" in result.output
    assert "ros2_list_topics" in result.output
    assert "demo complete" in result.output


def test_demo_tool_table_structure(runner):
    """Test that tool inventory table has proper structure."""
    result = runner.invoke(app, ["demo"])
    assert result.exit_code == 0
    # Check for table formatting characters
    assert "┏" in result.output or "━" in result.output or "┃" in result.output
    # Check for tool descriptions
    assert "Switch between mock and live mode" in result.output
    assert "Backend health check" in result.output
