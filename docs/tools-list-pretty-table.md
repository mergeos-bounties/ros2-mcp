#!/usr/bin/env python3
"""CLI tool to display ROS2 MCP tools in a pretty table format."""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

try:
    from prettytable import PrettyTable
except ImportError:
    print("Error: prettytable is not installed. Install it with: pip install prettytable", file=sys.stderr)
    sys.exit(1)


def load_tools_config() -> List[Dict[str, Any]]:
    """Load tools configuration from the MCP server config."""
    config_path = Path(__file__).parent.parent / "src" / "ros2_mcp" / "server.py"
    
    # Default tools if config cannot be loaded
    default_tools = [
        {
            "name": "ros2_topic_list",
            "description": "List all available ROS2 topics",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "ros2_topic_echo",
            "description": "Echo messages from a ROS2 topic",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Topic name to echo"},
                    "count": {"type": "integer", "description": "Number of messages to echo (optional)"}
                },
                "required": ["topic"]
            }
        },
        {
            "name": "ros2_topic_info",
            "description": "Get information about a ROS2 topic",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Topic name"}
                },
                "required": ["topic"]
            }
        },
        {
            "name": "ros2_topic_pub",
            "description": "Publish a message to a ROS2 topic",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Topic name"},
                    "msg_type": {"type": "string", "description": "Message type"},
                    "message": {"type": "string", "description": "Message content in YAML format"}
                },
                "required": ["topic", "msg_type", "message"]
            }
        },
        {
            "name": "ros2_node_list",
            "description": "List all active ROS2 nodes",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "ros2_node_info",
            "description": "Get detailed information about a ROS2 node",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"}
                },
                "required": ["node"]
            }
        },
        {
            "name": "ros2_service_list",
            "description": "List all available ROS2 services",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "ros2_service_call",
            "description": "Call a ROS2 service",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "service": {"type": "string", "description": "Service name"},
                    "srv_type": {"type": "string", "description": "Service type"},
                    "request": {"type": "string", "description": "Request data in YAML format"}
                },
                "required": ["service", "srv_type"]
            }
        },
        {
            "name": "ros2_param_get",
            "description": "Get a parameter value from a ROS2 node",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "param": {"type": "string", "description": "Parameter name"}
                },
                "required": ["node", "param"]
            }
        },
        {
            "name": "ros2_param_set",
            "description": "Set a parameter value on a ROS2 node",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "param": {"type": "string", "description": "Parameter name"},
                    "value": {"type": "string", "description": "Parameter value"}
                },
                "required": ["node", "param", "value"]
            }
        },
        {
            "name": "ros2_bag_record",
            "description": "Record ROS2 topics to a bag file",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "topics": {"type": "string", "description": "Space-separated topic names"},
                    "output": {"type": "string", "description": "Output bag file path"}
                },
                "required": ["topics", "output"]
            }
        },
        {
            "name": "ros2_bag_play",
            "description": "Play back a ROS2 bag file",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "bag_file": {"type": "string", "description": "Path to bag file"}
                },
                "required": ["bag_file"]
            }
        },
        {
            "name": "ros2_bag_info",
            "description": "Get information about a ROS2 bag file",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "bag_file": {"type": "string", "description": "Path to bag file"}
                },
                "required": ["bag_file"]
            }
        }
    ]
    
    return default_tools


def format_parameters(schema: Dict[str, Any]) -> str:
    """Format input schema parameters into a readable string."""
    if not schema or "properties" not in schema:
        return "None"
    
    props = schema["properties"]
    required = schema.get("required", [])
    
    if not props:
        return "None"
    
    params = []
    for name, details in props.items():
        param_type = details.get("type", "string")
        is_required = name in required
        req_marker = "*" if is_required else ""
        params.append(f"{name}{req_marker}: {param_type}")
    
    return "\n".join(params)


def create_tools_table(tools: List[Dict[str, Any]]) -> PrettyTable:
    """Create a pretty table with tools information."""
    table = PrettyTable()
    table.field_names = ["Tool Name", "Description", "Parameters"]
    table.align["Tool Name"] = "l"
    table.align["Description"] = "l"
    table.align["Parameters"] = "l"
    table.max_width["Description"] = 50
    table.max_width["Parameters"] = 40
    
    for tool in tools:
        name = tool.get("name", "Unknown")
        description = tool.get("description", "No description")
        params = format_parameters(tool.get("inputSchema", {}))
        
        table.add_row([name, description, params])
    
    return table


def main():
    """Main entry point for the tools list command."""
    print("ROS2 MCP Tools Inventory")
    print("=" * 80)
    print()
    
    tools = load_tools_config()
    table = create_tools_table(tools)
    
    print(table)
    print()
    print(f"Total tools: {len(tools)}")
    print("Note: Parameters marked with * are required")


if __name__ == "__main__":
    main()