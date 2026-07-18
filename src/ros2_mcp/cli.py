from __future__ import annotations

import json
from typing import Any, Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from ros2_mcp import __version__
from ros2_mcp.backend import get_backend, switch_mode
from ros2_mcp.config import get_mode, set_mode

app = typer.Typer(help="ros2-mcp — MCP server for ROS2", no_args_is_help=True)
tools_app = typer.Typer(help="List / probe tools")
app.add_typer(tools_app, name="tools")
console = Console()


@app.command("version")
def version_cmd() -> None:
    rprint({"version": __version__, "mode": get_mode()})


@app.command("doctor")
def doctor_cmd() -> None:
    """Backend health + mode + publish allowlist (if set)."""
    from ros2_mcp.config import domain_id, pub_allowlist, ros2_bin

    b = get_backend()
    info = b.doctor()
    info["ros2_mcp_version"] = __version__
    info["mode"] = get_mode()
    info["pub_allowlist"] = pub_allowlist()
    info["ros2_bin"] = ros2_bin()
    info["domain_id"] = domain_id()
    rprint(info)


@app.command("demo")
def demo_cmd() -> None:
    """Offline smoke: seed mock graph and exercise core APIs."""
    set_mode("mock")
    b = get_backend()
    b.seed_demo()
    rprint(b.doctor())
    topics = b.list_topics()
    rprint({"topics": len(topics), "sample": topics[:5]})
    nodes = b.list_nodes()
    rprint({"nodes": nodes})
    pub = b.topic_pub(
        "/turtle1/cmd_vel",
        "geometry_msgs/msg/Twist",
        {"linear": {"x": 0.5, "y": 0.0, "z": 0.0}, "angular": {"x": 0.0, "y": 0.0, "z": 0.3}},
        times=3,
    )
    rprint({"pub": pub})
    echo = b.topic_echo("/turtle1/pose", count=2)
    rprint({"pose_echo": echo})
    svc = b.service_call("/spawn", "turtlesim/srv/Spawn", {"name": "turtle2", "x": 2.0, "y": 3.0})
    rprint({"spawn": svc})
    rprint({"graph": b.graph_summary()})
    rprint({"tf": b.tf_tree()})
    rprint({"actions": b.list_actions()})
    rprint(
        {
            "nav_goal": b.action_send_goal(
                "/navigate_to_pose",
                "nav2_msgs/action/NavigateToPose",
                {"x": 3.0, "y": 4.0},
            )
        }
    )
    rprint("ros2-mcp demo complete (mock).")


@tools_app.command("list")
def tools_list() -> None:
    from ros2_mcp.server import mcp

    table = Table(title="ros2-mcp tools")
    table.add_column("Tool")
    # FastMCP stores tools internally
    names: list[str] = []
    try:
        # mcp 1.x: _tool_manager.list_tools() may be async; use known registry
        tools = getattr(mcp, "_tool_manager", None)
        if tools is not None:
            listed = getattr(tools, "_tools", {}) or {}
            names = sorted(listed.keys())
    except Exception:
        names = []
    if not names:
        names = [
            "ros2_mode",
            "ros2_doctor",
            "ros2_seed_demo",
            "ros2_list_topics",
            "ros2_topic_info",
            "ros2_topic_echo",
            "ros2_topic_pub",
            "ros2_list_nodes",
            "ros2_node_info",
            "ros2_list_services",
            "ros2_service_call",
            "ros2_list_params",
            "ros2_get_param",
            "ros2_set_param",
            "ros2_graph_summary",
            "ros2_tf_tree",
            "ros2_bag_info",
            "ros2_list_actions",
            "ros2_action_send_goal",
        ]
    for n in names:
        table.add_row(n)
    console.print(table)


@app.command("call")
def call_cmd(
    tool: str = typer.Argument(..., help="Short name e.g. list_topics or ros2_list_topics"),
    arg: Optional[list[str]] = typer.Argument(None, help="key=value pairs"),
    json_file: Optional[str] = typer.Option(
        None, "--json-file", help="Path to JSON file with tool arguments (merged with key=value pairs)"
    ),
) -> None:
    """One-shot mock/live tool call without MCP host."""
    b = get_backend()
    name = tool if tool.startswith("ros2_") else f"ros2_{tool}"
    kv: dict[str, Any] = {}
    for a in arg or []:
        if "=" in a:
            k, v = a.split("=", 1)
            try:
                kv[k] = json.loads(v)
            except json.JSONDecodeError:
                kv[k] = v
    if json_file:
        with open(json_file, "r", encoding="utf-8") as fh:
            file_args = json.load(fh)
        if not isinstance(file_args, dict):
            raise typer.BadParameter("--json-file must contain a JSON object")
        kv.update(file_args)

    dispatch = {
        "ros2_mode": lambda: switch_mode(str(kv.get("mode", get_mode()))),
        "ros2_doctor": b.doctor,
        "ros2_seed_demo": b.seed_demo,
        "ros2_list_topics": b.list_topics,
        "ros2_list_nodes": b.list_nodes,
        "ros2_list_services": b.list_services,
        "ros2_graph_summary": b.graph_summary,
        "ros2_tf_tree": b.tf_tree,
        "ros2_bag_info": lambda: b.bag_info(kv.get("path")),
        "ros2_list_actions": b.list_actions,
        "ros2_action_send_goal": lambda: b.action_send_goal(
            str(kv.get("action", "/navigate_to_pose")),
            str(kv.get("action_type", "nav2_msgs/action/NavigateToPose")),
            kv.get("goal") if isinstance(kv.get("goal"), dict) else {"x": 1.0, "y": 2.0},
        ),
        "ros2_topic_info": lambda: b.topic_info(str(kv.get("topic", "/cmd_vel"))),
        "ros2_topic_echo": lambda: b.topic_echo(
            str(kv.get("topic", "/turtle1/pose")), int(kv.get("count", 1))
        ),
        "ros2_topic_pub": lambda: b.topic_pub(
            str(kv.get("topic", "/turtle1/cmd_vel")),
            str(kv.get("msg_type", "geometry_msgs/msg/Twist")),
            kv.get("data")
            if isinstance(kv.get("data"), dict)
            else {"linear": {"x": 0.2}, "angular": {"z": 0.1}},
            int(kv.get("times", 1)),
        ),
        "ros2_node_info": lambda: b.node_info(str(kv.get("node", "/turtlesim"))),
        "ros2_service_call": lambda: b.service_call(
            str(kv.get("service", "/clear")),
            str(kv.get("srv_type", "std_srvs/srv/Empty")),
            kv.get("request") if isinstance(kv.get("request"), dict) else {},
        ),
        "ros2_list_params": lambda: b.list_params(kv.get("node")),
        "ros2_get_param": lambda: b.get_param(
            str(kv.get("node", "/turtlesim")), str(kv.get("name", "background_r"))
        ),
        "ros2_set_param": lambda: b.set_param(
            str(kv.get("node", "/turtlesim")),
            str(kv.get("name", "background_r")),
            kv.get("value", 100),
        ),
    }
    if name not in dispatch:
        raise typer.BadParameter(f"unknown tool {name}")
    rprint(dispatch[name]())


@app.command("serve")
def serve_cmd(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Log structured tool calls (JSON) to stderr; stdout stays MCP-only.",
    ),
) -> None:
    """Run MCP server over stdio (for Grok / Cursor / Claude)."""
    from ros2_mcp.server import run_stdio

    run_stdio(verbose=verbose)


def main() -> None:
    app()


if __name__ == "__main__":
    app()

# ---------------------------------------------------------------------------
# New command: tf-tree
# ---------------------------------------------------------------------------
@app.command("tf-tree")
def tf_tree_cmd() -> None:
    """Print the TF tree in a human‑readable format.

    The mock backend already provides a ``tf_tree`` method returning a dictionary
    with ``root`` and a list of ``frames``. This command formats that data into a
    simple tree view for quick inspection.
    """
    b = get_backend()
    tree = b.tf_tree()
    if not tree.get("ok"):
        # If the backend could not produce a TF tree, forward the error payload.
        rprint({"error": "Unable to retrieve TF tree", **tree})
        return

    # Header showing the root frame
    rprint({"root": tree.get("root")})
    # Each frame mapping: parent -> child with optional transform data.
    for frame in tree.get("frames", []):
        parent = frame.get("parent")
        child = frame.get("child")
        xyz = frame.get("xyz")
        rpy = frame.get("rpy")
        rprint({"link": f"{parent} -> {child}", "xyz": xyz, "rpy": rpy})
