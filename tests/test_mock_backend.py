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


def test_mock_bag_info_fixture():
    b = MockBackend()
    info = b.bag_info()
    assert info["ok"] is True
    assert info["mode"] == "mock"
    assert info["storage_id"] == "mcap"
    assert info["messages"] == 84
    assert any(t["name"] == "/turtle1/pose" for t in info["topics"])


def test_seed_fleet_profile():
    """Test multi-robot fleet graph seeding (Issue #4)."""
    b = MockBackend()
    result = b.seed_demo(profile="fleet")
    assert result["ok"] is True
    assert result["profile"] == "fleet"
    assert result["robots"] == 3

    # Verify 3 robots with namespaced topics
    topics = b.list_topics()
    for i in range(3):
        assert any(t["name"] == f"/robot{i}/cmd_vel" for t in topics), f"missing /robot{i}/cmd_vel"
        assert any(t["name"] == f"/robot{i}/odom" for t in topics), f"missing /robot{i}/odom"
        assert any(t["name"] == f"/robot{i}/scan" for t in topics), f"missing /robot{i}/scan"

    # Verify 3 diffs: wheel_radius differs per robot
    params = b.list_params()
    radii = [p["value"] for p in params if p["name"] == "wheel_radius"]
    assert len(radii) == 3, f"expected 3 wheel_radius params, got {len(radii)}"
    assert all("full_name" in p for p in params)
    assert radii == [0.05, 0.06, 0.07], f"wheel_radius values should differ: {radii}"

    # Verify fleet nodes exist
    nodes = b.list_nodes()
    for i in range(3):
        assert f"/robot{i}/controller" in nodes
        assert f"/robot{i}/diff_drive" in nodes
        assert f"/robot{i}/lidar" in nodes
