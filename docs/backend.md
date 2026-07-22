# Backend Implementations

ros2-mcp supports multiple backend implementations:

## Rclpy Backend

The rclpy backend uses the Python ROS2 client library (rclpy) for direct interaction with ROS2 systems. This provides the most efficient and feature-rich experience when rclpy is available.

### Availability

The rclpy backend will be automatically selected when:
1. The `ROS2_MCP_MODE` environment variable is set to 'rclpy'
2. The 'auto' mode is selected and rclpy is importable

### Fallback

When rclpy is not available, the backend will automatically fall back to the CLI backend.

## CLI Backend

The CLI backend uses the standard ROS2 command-line tools to interact with ROS2 systems. This provides a reliable fallback when rclpy is not available.

## Mock Backend

The mock backend is used for testing and demonstration purposes. It simulates a ROS2 system without requiring an actual ROS2 installation.

## Configuration

The backend can be configured using the `ROS2_MCP_MODE` environment variable:

- `auto`: Automatically select the best available backend (default)
- `rclpy`: Force use of the rclpy backend
- `cli`: Force use of the CLI backend
- `mock`: Force use of the mock backend