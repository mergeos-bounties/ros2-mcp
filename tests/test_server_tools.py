import json

from ros2_mcp.config import set_mode
from ros2_mcp.server import (
    ros2_doctor,
    ros2_bag_info,
    ros2_graph_summary,
    ros2_list_nodes,
    ros2_list_params,
    ros2_list_topics,
    ros2_mode,
    ros2_seed_demo,
    ros2_topic_echo,
    ros2_topic_pub,
)


def test_tools_mock_flow():
    set_mode("mock")
    assert "mock" in ros2_mode(None)
    assert json.loads(ros2_seed_demo())["ok"] is True
    doc = json.loads(ros2_doctor())
    assert doc["ok"] is True
    topics = json.loads(ros2_list_topics())
    assert isinstance(topics, list) and len(topics) >= 3
    nodes = json.loads(ros2_list_nodes())
    assert "/turtlesim" in nodes
    params = json.loads(ros2_list_params(None))
    assert any(p["full_name"] == "/turtlesim:background_r" for p in params)
    pub = json.loads(
        ros2_topic_pub(
            "/turtle1/cmd_vel",
            "geometry_msgs/msg/Twist",
            json.dumps({"linear": {"x": 0.2}, "angular": {"z": 0.1}}),
            2,
        )
    )
    assert pub["ok"] is True
    echo = json.loads(ros2_topic_echo("/turtle1/pose", 1))
    assert isinstance(echo, list)
    graph = json.loads(ros2_graph_summary())
    assert graph["mode"] == "mock"
    assert "ros2_mcp_version" in graph
    bag = json.loads(ros2_bag_info())
    assert bag["ok"] is True
    assert bag["mode"] == "mock"
    assert any(t["name"] == "/scan" for t in bag["topics"])
