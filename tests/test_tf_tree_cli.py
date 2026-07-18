"""Test the tf-tree CLI command."""
import os
import subprocess
import sys


def test_tf_tree_cli() -> None:
    """Run `ros2-mcp tf-tree` in mock mode and verify it returns map->odom->base_link."""
    env = os.environ.copy()
    env["PYTHONPATH"] = "/opt/data/workspace/mergeos-bounties-ros2-mcp/src"
    # Use the correct import path and run the command directly
    result = subprocess.run(
        [sys.executable, "-c", """
import sys
sys.path.insert(0, '/opt/data/workspace/mergeos-bounties-ros2-mcp/src')
from ros2_mcp.cli import app
sys.argv = ['ros2_mcp', 'tf-tree']
app()
"""],
        capture_output=True,
        text=True,
        cwd="/opt/data/workspace/mergeos-bounties-ros2-mcp",
        env=env,
    )
    output = result.stdout + result.stderr
    assert result.returncode == 0, f"CLI failed: {output}"
    assert "root" in output.lower() or "map" in output.lower(), f"Missing root/map in: {output}"
    assert "base_link" in output.lower(), f"Missing base_link in: {output}"
    assert "odom" in output.lower(), f"Missing odom in: {output}"
