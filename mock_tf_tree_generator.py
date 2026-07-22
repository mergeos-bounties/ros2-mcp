from typing import Dict, List, Tuple, Any
import numpy as np

class MockTFTreeGenerator:
    """
    A utility class designed to generate a programmatic, in-memory representation 
    of the ROS 2 Transform (TF) tree structure. This is crucial for mocking 
    complex multi-branch sensor setups and ensuring deterministic unit testing 
    without requiring a live rviz/tf service.

    The generated graph maps each frame_id to its parent frames, allowing 
    for comprehensive traversal and path validation.
    """

    def __init__(self):
        """Initializes the mock graph structure."""
        # Structure: {frame_id: {'parent': parent_id, 'transforms': dict_of_mock_transforms}}
        self.mock_graph: Dict[str, Any] = {}

    def add_link(self, frame_id: str, parent_id: str) -> None:
        """
        Adds a node (frame) and defines its immediate parent in the TF tree.

        Args:
            frame_id (str): The ID of the new link/frame (e.g., 'camera_link').
            parent_id (str): The ID of the frame that is the direct parent 
                             of this link (must already exist or be root).

        Raises:
            ValueError: If the parent_id does not correspond to a known node 
                        in the graph structure.
        """
        if parent_id not in self.mock_graph and parent_id != "map":
             # Allow 'map' as an assumed global root if not explicitly added
            raise ValueError(f"Parent frame ID '{parent_id}' is unknown or has not been linked.")

        self.mock_graph[frame_id] = {
            'parent': parent_id, 
            'transforms': {}
        }
    
    def set_mock_transform(self, child_frame: str, parent_frame: str, transform_data: Dict) -> None:
        """
        Assigns mock transformation parameters (e.g., XYZ, RollPitchYaw) 
        between a parent and child frame pair.

        Args:
            child_frame (str): The descendant link receiving the transform data.
            parent_frame (str): The ancestor link providing the reference frame.
            transform_data (Dict[str, Any]): Dictionary containing mock values.
                                              Expected keys include 'translation' 
                                              (list/tuple of length 3) and 
                                              'rotation' (quaternion or rpy).
        """
        if child_frame not in self.mock_graph:
            raise KeyError(f"Child frame '{child_frame}' must be linked via add_link() first.")

        # Simple validation to ensure parent integrity is maintained 
        # although the transform itself might span across distant ancestors.
        if parent_frame != self.mock_graph[child_frame]['parent']:
             print(f"[Warning] Setting transform from '{parent_frame}' to '{child_frame}'. "
                   "This may break graph hierarchy rules if they are not adjacent.")

        self.mock_graph[child_frame]['transforms'][parent_frame] = transform_data


    def generate_full_tf_path(self, start_frame: str, end_frame: str) -> List[Tuple[str, Any]]:
        """
        Traverses the defined mock graph from a starting frame to an ending frame 
        to construct the necessary chain of transforms.

        Args:
            start_frame (str): The root or initial reference frame (e.g., 'map').
            end_frame (str): The final target frame (e.g., 'camera_link').

        Returns:
            List[Tuple[str, Any]]: An ordered list of (parent_child_pair, transform) 
                                    representing the concatenated transforms. Returns empty list if path is broken.
        """
        if start_frame not in self.mock_graph and start_frame != "map":
             return []

        path = []
        current_node = end_frame
        current_parent = None
        
        # Step 1: Trace the parent chain back to the root (or starting node)
        chain: List[str] = []
        while current_node and current_node != start_frame:
            if current_node not in self.mock_graph or 'parent' not in self.mock_graph[current_node]:
                break # Broken link
            
            parent = self.mock_graph[current_node]['parent']
            chain.append((parent, current_node)) 
            current_node = parent

        # Step 2: Check if the starting frame matches the traced root of the path
        if chain and chain[-1][0] == start_frame:
             path = [(p, c, self.mock_graph[c]['transforms'].get(p)) for p, c in reversed(chain)]
        elif current_node != start_frame and end_frame == start_frame:
            return [] # Invalid path if nothing was linked

        return path


# ================================================================
# Unit Test Section (Mandatory Acceptance Component)
# ================================================================

def test_mock_tf_tree_generator() -> None:
    """
    Comprehensive unit tests validating the functionality of MockTFTreeGenerator. 
    Tests must ensure graph traversal and structured data output are correct.
    """
    print("\n--- Running Unit Tests for MockTFTreeGenerator ---")

    # Scenario setup: Map -> Base -> Body -> Camera
    generator = MockTFTreeGenerator()
    try:
        # Linking nodes (Topology definition)
        generator.add_link("base_link", "map")
        generator.add_link("body", "base_link")
        generator.add_link("camera_link", "body")

        # Setting mock transforms (Parameterization of links)
        # Map -> Base
        generator.set_mock_transform(child_frame="base_link", parent_frame="map", 
                                     transform_data={'translation': [0.0, 0.0, 1.0]})
        # Base -> Body
        generator.set_mock_transform(child_frame="body", parent_frame="base_link", 
                                     transform_data={'rotation': 'rpy'})
        # Body -> Camera
        generator.set_mock_transform(child_frame="camera_link", parent_frame="body", 
                                     transform_data={'translation': [0.1, 0.2, 0.0]})

    except (ValueError, KeyError) as e:
        print(f"TEST FAILED during setup: {e}")


    # Test Case 1: Successful full path traversal
    start = "map"
    end = "camera_link"
    path_transforms = generator.generate_full_tf_path(start, end)

    print("\n[SUCCESS] Test Case 1: Full Traversal (map -> camera_link)")
    assert len(path_transforms) == 3, f"Expected 3 steps, got {len(path_transforms)}"
    # Check the final link transformation data integrity
    last_step = path_transforms[-1]
    assert last_step[2]['translation'] == [0.1, 0.2, 0.0], "Final transform translation mismatch."
    print("  -> Traversal structure and data confirmed correct.")


    # Test Case 2: Short path traversal (map -> base)
    start = "map"
    end = "base_link"
    path_transforms_short = generator.generate_full_tf_path(start, end)

    print("\n[SUCCESS] Test Case 2: Short Traversal (map -> base_link)")
    assert len(path_transforms_short) == 1, f"Expected 1 step, got {len(path_transforms_short)}"
    # Check the initial link transformation data integrity
    first_step = path_transforms_short[0]
    assert first_step[2]['translation'] == [0.0, 0.0, 1.0], "Initial transform translation mismatch."
    print("  -> Short path validated correctly.")


    # Test Case 3: Broken/Non-existent path (Should return empty list)
    start = "map"
    end = "non_existent_link"
    path_broken = generator.generate_full_tf_path(start, end)

    print("\n[SUCCESS] Test Case 3: Broken Path Traversal")
    assert path_broken == [], "Expected empty list for broken path."
    print("  -> Handling of invalid terminal nodes confirmed correct.")


# --- Execute Tests ---
test_mock_tf_tree_generator()
