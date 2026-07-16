from typer.testing import CliRunner

from ros2_mcp.cli import app, build_tool_table


runner = CliRunner()


def test_build_tool_table_numbers_tools():
    table = build_tool_table(["ros2_doctor", "ros2_list_topics"], title="inventory")

    assert table.title == "inventory"
    assert [column.header for column in table.columns] == ["#", "Tool"]
    assert table.row_count == 2


def test_demo_prints_tool_inventory_table():
    result = runner.invoke(app, ["demo"])

    assert result.exit_code == 0, result.output
    assert "ros2-mcp demo tool inventory" in result.output
    assert "ros2_doctor" in result.output
    assert "ros2_list_topics" in result.output
    assert "ros2-mcp demo complete" in result.output


def test_tools_list_prints_numbered_inventory():
    result = runner.invoke(app, ["tools", "list"])

    assert result.exit_code == 0, result.output
    assert "ros2-mcp tools" in result.output
    assert "ros2_doctor" in result.output
    assert "ros2_action_send_goal" in result.output
