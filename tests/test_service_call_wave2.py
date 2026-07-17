"""Service call wave2 fixture: extended samples are readable and parseable."""
from pathlib import Path


def test_service_call_wave2_has_extended_services() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "service_call_wave2.txt"
    text = p.read_text(encoding="utf-8")
    # Wave1 services
    assert "/add_two_ints" in text
    assert "/spawn" in text
    # Wave2 extended services
    assert "/clear" in text
    assert "/reset" in text
    assert "/get_loggers" in text
    assert "/set_logger_level" in text
    assert "/parameter_events" in text


def test_service_call_wave2_rcl_interfaces() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "service_call_wave2.txt"
    text = p.read_text(encoding="utf-8")
    assert "rcl_interfaces/srv/GetLoggers" in text
    assert "rcl_interfaces/srv/SetLoggerLevel" in text


def test_service_call_wave2_turtlesim_services() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "service_call_wave2.txt"
    text = p.read_text(encoding="utf-8")
    assert "turtlesim/srv/Clear" in text
    assert "turtlesim/srv/Reset" in text
