from ros2_mcp.backend.parsers import parse_node_list, parse_service_list


def test_parse_node_list() -> None:
    nodes = parse_node_list("/talker\nturtle1\n")
    assert "/talker" in nodes
    assert "/turtle1" in nodes


def test_parse_service_list() -> None:
    items = parse_service_list("/reset [std_srvs/srv/Empty]\n/spawn\n")
    assert items[0]["name"] == "/reset"
    assert items[0]["type"] == "std_srvs/srv/Empty"
    assert items[1]["name"] == "/spawn"
