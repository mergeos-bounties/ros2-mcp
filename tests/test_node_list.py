import os

def test_node_list_sample():
    fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'node_list_sample.txt')
    assert os.path.exists(fixture_path), "Fixture file not found"
    
    with open(fixture_path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
        
    assert len(lines) == 5, "Expected 5 mock nodes in the sample"
    assert "/camera/camera_node" in lines, "Missing expected node /camera/camera_node"
    assert "/controller_manager" in lines, "Missing expected node /controller_manager"
