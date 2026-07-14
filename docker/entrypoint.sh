#!/usr/bin/env bash
set -euo pipefail

source /opt/ros/humble/setup.bash
export PATH="/opt/ros2-mcp/bin:${PATH}"

if [[ "$#" -eq 0 ]]; then
  set -- serve
fi

if [[ "$1" == "ros2-mcp" ]]; then
  exec "$@"
fi

exec ros2-mcp "$@"
