from ros2_mcp.backend.parsers import parse_topic_info_verbose


SAMPLE = """
Type: geometry_msgs/msg/Twist
Publisher count: 1
Subscription count: 2

Node name: /teleop
Endpoint type: PUBLISHER
Topic type: geometry_msgs/msg/Twist

Node name: /robot
Endpoint type: SUBSCRIPTION
"""


def test_parse_topic_info_verbose() -> None:
    r = parse_topic_info_verbose(SAMPLE, topic="/cmd_vel")
    assert r["ok"]
    assert r["type"] == "geometry_msgs/msg/Twist"
    assert r["publisher_count"] == 1
    assert r["subscription_count"] == 2
    assert any(p.get("node") == "/teleop" for p in r["publishers"])
