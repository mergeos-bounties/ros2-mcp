FROM ros:humble-ros-base-jammy

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    ROS2_MCP_MODE=mock \
    PATH="/opt/ros2-mcp/bin:${PATH}"

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        software-properties-common \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        git \
        python3.11 \
        python3.11-dev \
        python3.11-venv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY src ./src

RUN python3.11 -m venv /opt/ros2-mcp \
    && /opt/ros2-mcp/bin/python -m ensurepip --upgrade \
    && /opt/ros2-mcp/bin/pip install --no-cache-dir --upgrade pip setuptools wheel \
    && /opt/ros2-mcp/bin/pip install --no-cache-dir .

COPY docker/entrypoint.sh /ros2-mcp-entrypoint.sh
RUN chmod +x /ros2-mcp-entrypoint.sh

ENTRYPOINT ["/ros2-mcp-entrypoint.sh"]
CMD ["serve"]
