"""Topic echo wave2 fixture: extended samples are readable and parseable."""
from pathlib import Path


def test_topic_echo_wave2_has_extended_samples() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "topic_echo_wave2.txt"
    text = p.read_text(encoding="utf-8")
    # Wave1 topics
    assert "/cmd_vel" in text
    assert "/scan" in text
    # Wave2 extended topics
    assert "/imu" in text
    assert "/joint_states" in text
    assert "/battery_state" in text
    # Wave2 specific fields
    assert "angle_min" in text
    assert "orientation" in text
    assert "percentage" in text


def test_topic_echo_wave2_imu_fields() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "topic_echo_wave2.txt"
    text = p.read_text(encoding="utf-8")
    assert "sensor_msgs/msg/Imu" in text
    assert "linear_acceleration" in text
    assert "gravity" in text or "9.81" in text


def test_topic_echo_wave2_joint_states() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "topic_echo_wave2.txt"
    text = p.read_text(encoding="utf-8")
    assert "sensor_msgs/msg/JointState" in text
    assert "position" in text
    assert "velocity" in text
