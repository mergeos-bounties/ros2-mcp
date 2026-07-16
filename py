Based on the repository context and the issue description, here is the complete solution to implement a readable table for listing available MCP tools in the demo command.

The solution involves two main changes:
1.  **`src/ros2_mcp/cli.py`**: Update the `demo()` function to use a new helper that formats tool definitions into a Markdown-style table instead of just printing raw JSON or strings.
2.  **`tests/test_cli.py`**: Add unit tests to verify the table formatting logic works correctly with various tool configurations.