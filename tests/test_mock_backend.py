from ros2_mcp.backend.mock import MockBackend
from ros2_mcp.config import set_mode
from ros2_mcp.backend import get_backend


def test_seed_and_list():
    b = MockBackend()
    s = b.seed_demo()
    assert s["ok"]
    topics = b.list_topics()
    assert any(t["name"] == "/cmd_vel" for t in topics)
    assert "/turtlesim" in b.list_nodes()
    assert any(s["name"] == "/spawn" for s in b.list_services())


def test_pub_moves_pose():
    b = MockBackend()
    b.seed_demo()
    before = b.topic_echo("/turtle1/pose", 1)[0]["data"]
    b.topic_pub(
        "/turtle1/cmd_vel",
        "geometry_msgs/msg/Twist",
        {"linear": {"x": 1.0}, "angular": {"z": 0.0}},
        times=5,
    )
    after = b.topic_echo("/turtle1/pose", 1)[0]["data"]
    assert after["x"] != before["x"] or after["y"] != before["y"] or after.get("linear_velocity")


def test_params_and_service():
    b = MockBackend()
    b.seed_demo()
    g = b.get_param("/turtlesim", "background_r")
    assert g["ok"]
    b.set_param("/turtlesim", "background_r", 10)
    assert b.get_param("/turtlesim", "background_r")["value"] == 10
    r = b.service_call("/spawn", "turtlesim/srv/Spawn", {"name": "hero"})
    assert r["ok"]
    assert any("hero" in n for n in b.list_nodes())


def test_get_backend_mock():
    set_mode("mock")
    assert get_backend().name == "mock"


def test_tf_tree_and_actions():
    b = MockBackend()
    b.seed_demo()
    tree = b.tf_tree()
    assert tree["ok"] is True
    assert tree["root"] == "map"
    assert any(f["child"] == "base_link" for f in tree["frames"])
    acts = b.list_actions()
    assert any(a["name"] == "/navigate_to_pose" for a in acts)
    r = b.action_send_goal("/navigate_to_pose", "nav2_msgs/action/NavigateToPose", {"x": 1.0, "y": 2.0})
    assert r["ok"] is True
    assert r["status"] == "SUCCEEDED"
