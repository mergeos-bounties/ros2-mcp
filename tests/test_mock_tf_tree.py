"""Tests for mock_tf_tree tool."""

from ros2_mcp.backend.mock import mock_tf_tree


def test_tf_tree_structure():
    result = mock_tf_tree()
    assert result["ok"] is True
    assert result["frame_count"] == 3
    assert result["tree"] == "map -> odom -> base_link"


def test_tf_tree_frames():
    result = mock_tf_tree()
    frames = result["frames"]
    assert "map" in frames
    assert "odom" in frames
    assert "base_link" in frames
    assert frames["map"]["parent"] is None
    assert frames["odom"]["parent"] == "map"
    assert frames["base_link"]["parent"] == "odom"
    assert "base_link" in frames["odom"]["children"]
    assert frames["base_link"]["children"] == []


def test_tf_tree_translation():
    result = mock_tf_tree()
    frames = result["frames"]
    assert len(frames["odom"]["translation"]) == 3
    assert all(isinstance(v, (int, float)) for v in frames["map"]["translation"])
    assert len(frames["base_link"]["rotation"]) == 4
