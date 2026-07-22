"""TF frame tree sample fixture is readable."""
from pathlib import Path

from ros2_mcp.backend.parsers import parse_tf_frames


def test_tf_frame_tree_sample_exists() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "tf_frame_tree_sample.txt"
    text = p.read_text(encoding="utf-8")
    assert "base_link" in text
    assert "laser_link" in text
    assert "camera_optical_frame" in text


def test_tf_frame_tree_sample_parses_frame_names() -> None:
    p = Path(__file__).resolve().parents[1] / "examples" / "tf_frame_tree_sample.txt"
    frames = parse_tf_frames(p.read_text(encoding="utf-8"))

    assert frames == [
        "map",
        "odom",
        "base_link",
        "laser_link",
        "imu_link",
        "camera_link",
        "camera_optical_frame",
    ]
