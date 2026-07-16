import os

def test_bag_info_sample():
    fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'bag_info_sample.txt')
    assert os.path.exists(fixture_path), "Fixture not found"
    
    with open(fixture_path, 'r') as f:
        content = f.read()
        
    assert "rosbag2" in content, "Missing rosbag identifier"
    assert "/camera/image_raw" in content, "Missing topic data"
    assert "Duration:" in content, "Missing duration metadata"
