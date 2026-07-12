from ros2_mcp.backend.parsers import parse_action_list, parse_node_list, parse_param_list, parse_service_list


def test_parse_node_list() -> None:
    nodes = parse_node_list("/talker\nturtle1\n")
    assert "/talker" in nodes
    assert "/turtle1" in nodes


def test_parse_service_list() -> None:
    items = parse_service_list("/reset [std_srvs/srv/Empty]\n/spawn\n")
    assert items[0]["name"] == "/reset"
    assert items[0]["type"] == "std_srvs/srv/Empty"
    assert items[1]["name"] == "/spawn"


def test_parse_action_list() -> None:
    items = parse_action_list("/fibonacci [example_interfaces/action/Fibonacci]\n/nav\n")
    assert items[0]["name"] == "/fibonacci"
    assert items[0]["type"] == "example_interfaces/action/Fibonacci"
    assert items[1]["name"] == "/nav"


def test_parse_param_list() -> None:
    items = parse_param_list("/talker.use_sim_time\n  qos_overrides\n")
    assert "/talker.use_sim_time" in items
    assert "qos_overrides" in items
