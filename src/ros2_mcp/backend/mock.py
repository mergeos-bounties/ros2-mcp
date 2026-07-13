"""Offline mock ROS2 graph for AI tools without a ROS install."""

from __future__ import annotations

import math
import time
from copy import deepcopy
from typing import Any


class MockBackend:
    name = "mock"

    def __init__(self) -> None:
        self._t0 = time.time()
        self.seed_demo()

    def seed_demo(self, profile: str = "default") -> dict[str, Any]:
        if profile == "fleet":
            return self._seed_fleet()
        self._topics: dict[str, dict[str, Any]] = {
            "/turtle1/cmd_vel": {
                "type": "geometry_msgs/msg/Twist",
                "publishers": ["/teleop_twist_keyboard"],
                "subscribers": ["/turtlesim"],
            },
            "/turtle1/pose": {
                "type": "turtlesim/msg/Pose",
                "publishers": ["/turtlesim"],
                "subscribers": ["/pose_logger"],
            },
            "/turtle1/color_sensor": {
                "type": "turtlesim/msg/Color",
                "publishers": ["/turtlesim"],
                "subscribers": [],
            },
            "/clock": {
                "type": "rosgraph_msgs/msg/Clock",
                "publishers": ["/mock_clock"],
                "subscribers": [],
            },
            "/scan": {
                "type": "sensor_msgs/msg/LaserScan",
                "publishers": ["/mock_lidar"],
                "subscribers": ["/slam_toolbox"],
            },
            "/cmd_vel": {
                "type": "geometry_msgs/msg/Twist",
                "publishers": ["/nav2_controller"],
                "subscribers": ["/diff_drive_controller"],
            },
            "/odom": {
                "type": "nav_msgs/msg/Odometry",
                "publishers": ["/diff_drive_controller"],
                "subscribers": ["/ekf_node"],
            },
            "/tf": {
                "type": "tf2_msgs/msg/TFMessage",
                "publishers": ["/robot_state_publisher"],
                "subscribers": [],
            },
        }
        self._nodes = {
            "/turtlesim": {
                "publishers": ["/turtle1/pose", "/turtle1/color_sensor"],
                "subscribers": ["/turtle1/cmd_vel"],
                "services": ["/spawn", "/kill", "/clear", "/reset"],
            },
            "/teleop_twist_keyboard": {
                "publishers": ["/turtle1/cmd_vel", "/cmd_vel"],
                "subscribers": [],
                "services": [],
            },
            "/mock_lidar": {
                "publishers": ["/scan"],
                "subscribers": [],
                "services": [],
            },
            "/diff_drive_controller": {
                "publishers": ["/odom"],
                "subscribers": ["/cmd_vel"],
                "services": [],
            },
            "/robot_state_publisher": {
                "publishers": ["/tf"],
                "subscribers": [],
                "services": [],
            },
        }
        self._services: dict[str, dict[str, Any]] = {
            "/spawn": {"type": "turtlesim/srv/Spawn"},
            "/kill": {"type": "turtlesim/srv/Kill"},
            "/clear": {"type": "std_srvs/srv/Empty"},
            "/reset": {"type": "std_srvs/srv/Empty"},
            "/turtle1/set_pen": {"type": "turtlesim/srv/SetPen"},
        }
        self._params: dict[str, dict[str, Any]] = {
            "/turtlesim": {
                "background_r": 69,
                "background_g": 86,
                "background_b": 255,
                "qos_overrides./parameter_events.publisher.depth": 1000,
            },
            "/diff_drive_controller": {
                "wheel_separation": 0.3,
                "wheel_radius": 0.05,
                "publish_rate": 50.0,
            },
        }
        # message buffers: topic -> list of {stamp, data}
        self._buf: dict[str, list[dict[str, Any]]] = {t: [] for t in self._topics}
        self._pose = {"x": 5.5, "y": 5.5, "theta": 0.0, "linear_velocity": 0.0, "angular_velocity": 0.0}
        self._push(
            "/turtle1/pose",
            {"x": self._pose["x"], "y": self._pose["y"], "theta": self._pose["theta"]},
        )
        self._push(
            "/scan",
            {
                "angle_min": -math.pi,
                "angle_max": math.pi,
                "ranges": [3.0 + 0.1 * math.sin(i) for i in range(36)],
            },
        )
        return {"ok": True, "mode": "mock", "topics": list(self._topics), "nodes": list(self._nodes)}

    def _seed_fleet(self) -> dict[str, Any]:
        """Seed a 3-robot fleet graph: robot0/robot1/robot2 with cmd_vel + odom namespaces.

        Each robot gets its own namespaced topics (/robotN/cmd_vel, /robotN/odom,
        /robotN/scan, /robotN/tf), nodes, and diff-drive params. The three robots
        differ by their diff-drive wheel_radius and grid offset (3 diffs).
        """
        self._topics = {}
        self._nodes = {}
        self._services = {}
        self._params = {}
        self._pose = {"x": 0.0, "y": 0.0, "theta": 0.0, "linear_velocity": 0.0, "angular_velocity": 0.0}
        fleet_offsets = [(0.0, 0.0), (3.0, 0.0), (0.0, 3.0)]
        for i in range(3):
            r = f"robot{i}"
            ox, oy = fleet_offsets[i]
            self._topics[f"/{r}/cmd_vel"] = {
                "type": "geometry_msgs/msg/Twist",
                "publishers": [f"/{r}/controller"],
                "subscribers": [f"/{r}/diff_drive"],
            }
            self._topics[f"/{r}/odom"] = {
                "type": "nav_msgs/msg/Odometry",
                "publishers": [f"/{r}/diff_drive"],
                "subscribers": [f"/{r}/ekf"],
            }
            self._topics[f"/{r}/scan"] = {
                "type": "sensor_msgs/msg/LaserScan",
                "publishers": [f"/{r}/lidar"],
                "subscribers": [f"/{r}/slam"],
            }
            self._topics[f"/{r}/tf"] = {
                "type": "tf2_msgs/msg/TFMessage",
                "publishers": [f"/{r}/robot_state_publisher"],
                "subscribers": [],
            }
            self._nodes[f"/{r}/controller"] = {"publishers": [f"/{r}/cmd_vel"], "subscribers": [], "services": []}
            self._nodes[f"/{r}/diff_drive"] = {"publishers": [f"/{r}/odom"], "subscribers": [f"/{r}/cmd_vel"], "services": []}
            self._nodes[f"/{r}/lidar"] = {"publishers": [f"/{r}/scan"], "subscribers": [], "services": []}
            self._nodes[f"/{r}/robot_state_publisher"] = {"publishers": [f"/{r}/tf"], "subscribers": [], "services": []}
            self._params[f"/{r}/diff_drive"] = {
                "wheel_separation": 0.3,
                "wheel_radius": round(0.05 + i * 0.01, 2),  # 3 diffs: 0.05, 0.06, 0.07
                "odom_frame": f"{r}/odom",
                "base_frame": f"{r}/base_link",
                "offset_x": ox,
                "offset_y": oy,
            }
        self._buf = {t: [] for t in self._topics}
        for i in range(3):
            r = f"robot{i}"
            self._push(f"/{r}/odom", {"pose": {"x": 0.0, "y": 0.0, "theta": 0.0}, "twist": {"linear_x": 0.0, "angular_z": 0.0}})
            self._push(f"/{r}/scan", {"angle_min": -math.pi, "angle_max": math.pi, "ranges": [3.0] * 36})
        return {"ok": True, "mode": "mock", "profile": "fleet", "robots": 3, "topics": list(self._topics), "nodes": list(self._nodes)}

    def _stamp(self) -> float:
        return round(time.time() - self._t0, 3)

    def _push(self, topic: str, data: dict[str, Any]) -> None:
        if topic not in self._buf:
            self._buf[topic] = []
        self._buf[topic].append({"stamp": self._stamp(), "data": data})
        if len(self._buf[topic]) > 50:
            self._buf[topic] = self._buf[topic][-50:]

    def doctor(self) -> dict[str, Any]:
        actions = getattr(self, "_actions", None)
        n_actions = len(actions) if actions is not None else 0
        return {
            "ok": True,
            "mode": "mock",
            "ros2_required": False,
            "message": "Mock backend active — no ROS2 install needed",
            "topics": len(self._topics),
            "nodes": len(self._nodes),
            "services": len(self._services),
            "actions": n_actions,
            "graph_summary": {
                "topics": len(self._topics),
                "nodes": len(self._nodes),
                "services": len(self._services),
                "actions": n_actions,
            },
            "sim_time_sec": round(time.time() - self._t0, 3),
            "clock_source": "mock_steady",
            "namespace_count": self._namespace_count(),
            "qos_summary": {
                "reliable": 3,
                "best_effort": 1,
                "depth_default": 10,
            },
        }

    def _namespace_count(self) -> int:
        ns: set[str] = set()
        for name in self._nodes:
            parts = str(name).strip("/").split("/")
            if len(parts) >= 2:
                ns.add(parts[0])
        return max(1, len(ns))

    def list_topics(self) -> list[dict[str, Any]]:
        return [{"name": n, "type": m["type"]} for n, m in sorted(self._topics.items())]

    def topic_info(self, topic: str) -> dict[str, Any]:
        if topic not in self._topics:
            return {"ok": False, "error": f"unknown topic {topic}"}
        meta = self._topics[topic]
        return {
            "ok": True,
            "name": topic,
            "type": meta["type"],
            "publishers": meta["publishers"],
            "subscribers": meta["subscribers"],
            "buffered": len(self._buf.get(topic, [])),
        }

    def topic_echo(self, topic: str, count: int = 1) -> list[dict[str, Any]]:
        if topic not in self._topics:
            return [{"error": f"unknown topic {topic}"}]
        # refresh synthetic pose/scan
        if topic == "/turtle1/pose":
            self._push("/turtle1/pose", deepcopy(self._pose))
        if topic == "/scan":
            t = self._stamp()
            self._push(
                "/scan",
                {
                    "angle_min": -math.pi,
                    "angle_max": math.pi,
                    "ranges": [2.5 + math.sin(t + i * 0.2) for i in range(36)],
                },
            )
        if topic == "/clock":
            self._push("/clock", {"sec": int(self._stamp()), "nanosec": 0})
        buf = self._buf.get(topic, [])
        if not buf:
            return [{"stamp": self._stamp(), "data": {}, "note": "no messages yet"}]
        n = max(1, min(count, 20))
        return list(reversed(buf[-n:]))

    def topic_pub(
        self,
        topic: str,
        msg_type: str,
        data: dict[str, Any],
        times: int = 1,
    ) -> dict[str, Any]:
        if topic not in self._topics:
            self._topics[topic] = {
                "type": msg_type,
                "publishers": ["/ros2_mcp"],
                "subscribers": [],
            }
            self._buf[topic] = []
        else:
            if msg_type and self._topics[topic]["type"] != msg_type:
                # allow override note
                pass
        n = max(1, min(times, 100))
        for _ in range(n):
            self._push(topic, data)
        # integrate cmd_vel-like messages into turtle pose
        if topic in ("/turtle1/cmd_vel", "/cmd_vel"):
            lin = float(data.get("linear", {}).get("x", data.get("linear_x", 0.0)) or 0.0)
            ang = float(data.get("angular", {}).get("z", data.get("angular_z", 0.0)) or 0.0)
            dt = 0.1
            self._pose["theta"] += ang * dt
            self._pose["x"] += lin * math.cos(self._pose["theta"]) * dt
            self._pose["y"] += lin * math.sin(self._pose["theta"]) * dt
            self._pose["linear_velocity"] = lin
            self._pose["angular_velocity"] = ang
            self._push("/turtle1/pose", deepcopy(self._pose))
            self._push("/odom", {"pose": deepcopy(self._pose), "twist": {"linear_x": lin, "angular_z": ang}})
        return {"ok": True, "topic": topic, "type": msg_type, "published": n, "last": data}

    def list_nodes(self) -> list[str]:
        return sorted(self._nodes.keys())

    def node_info(self, node: str) -> dict[str, Any]:
        if node not in self._nodes:
            # allow without leading slash
            alt = node if node.startswith("/") else f"/{node}"
            if alt not in self._nodes:
                return {"ok": False, "error": f"unknown node {node}"}
            node = alt
        info = self._nodes[node]
        return {"ok": True, "name": node, **info}

    def list_services(self) -> list[dict[str, Any]]:
        return [{"name": n, "type": m["type"]} for n, m in sorted(self._services.items())]

    def service_call(
        self,
        service: str,
        srv_type: str,
        request: dict[str, Any],
    ) -> dict[str, Any]:
        if service not in self._services:
            return {"ok": False, "error": f"unknown service {service}"}
        if service == "/spawn":
            name = request.get("name") or f"turtle{len(self._nodes)}"
            self._nodes[f"/{name}"] = {
                "publishers": [f"/{name}/pose"],
                "subscribers": [f"/{name}/cmd_vel"],
                "services": [],
            }
            return {"ok": True, "service": service, "response": {"name": name}}
        if service in ("/clear", "/reset"):
            self.seed_demo()
            return {"ok": True, "service": service, "response": {}}
        if service == "/kill":
            return {"ok": True, "service": service, "response": {}, "request": request}
        return {"ok": True, "service": service, "type": srv_type, "request": request, "response": {"success": True}}

    def list_params(self, node: str | None = None) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        nodes = [node] if node else list(self._params.keys())
        for n in nodes:
            key = n if n in self._params else (n if n.startswith("/") else f"/{n}")
            if key not in self._params:
                continue
            for pname, val in self._params[key].items():
                out.append({"node": key, "name": pname, "value": val})
        return out

    def get_param(self, node: str, name: str) -> dict[str, Any]:
        key = node if node in self._params else (node if node.startswith("/") else f"/{node}")
        if key not in self._params or name not in self._params[key]:
            return {"ok": False, "error": f"param {node}/{name} not found"}
        return {"ok": True, "node": key, "name": name, "value": self._params[key][name]}

    def set_param(self, node: str, name: str, value: Any) -> dict[str, Any]:
        key = node if node.startswith("/") else f"/{node}"
        self._params.setdefault(key, {})[name] = value
        return {"ok": True, "node": key, "name": name, "value": value}

    def graph_summary(self) -> dict[str, Any]:
        return {
            "mode": "mock",
            "topics": len(self._topics),
            "nodes": len(self._nodes),
            "services": len(self._services),
            "topic_names": sorted(self._topics.keys()),
            "node_names": sorted(self._nodes.keys()),
            "service_names": sorted(self._services.keys()),
            "turtle_pose": deepcopy(self._pose),
            "actions": [a["name"] for a in self.list_actions()],
        }

    def tf_tree(self) -> dict[str, Any]:
        """Static TF tree for mock robot (map → odom → base_link → sensors)."""
        return {
            "mode": "mock",
            "root": "map",
            "frames": [
                {"parent": "map", "child": "odom", "xyz": [0.0, 0.0, 0.0], "rpy": [0, 0, 0]},
                {
                    "parent": "odom",
                    "child": "base_link",
                    "xyz": [self._pose["x"] - 5.5, self._pose["y"] - 5.5, 0.0],
                    "rpy": [0, 0, self._pose["theta"]],
                },
                {"parent": "base_link", "child": "laser_link", "xyz": [0.1, 0.0, 0.15], "rpy": [0, 0, 0]},
                {"parent": "base_link", "child": "imu_link", "xyz": [0.0, 0.0, 0.05], "rpy": [0, 0, 0]},
            ],
            "ok": True,
        }

    def list_actions(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "/navigate_to_pose",
                "type": "nav2_msgs/action/NavigateToPose",
                "server": "/bt_navigator",
            },
            {
                "name": "/follow_path",
                "type": "nav2_msgs/action/FollowPath",
                "server": "/controller_server",
            },
            {
                "name": "/turtle1/rotate_absolute",
                "type": "turtlesim/action/RotateAbsolute",
                "server": "/turtlesim",
            },
        ]

    def action_send_goal(
        self,
        action: str,
        action_type: str,
        goal: dict[str, Any],
    ) -> dict[str, Any]:
        known = {a["name"] for a in self.list_actions()}
        if action not in known:
            return {"ok": False, "error": f"unknown action {action}", "known": sorted(known)}
        # mock: accept goal, optionally nudge pose toward target
        if action == "/navigate_to_pose":
            pose = goal.get("pose") or goal
            x = float(pose.get("x", pose.get("position", {}).get("x", self._pose["x"])))
            y = float(pose.get("y", pose.get("position", {}).get("y", self._pose["y"])))
            self._pose["x"] = x
            self._pose["y"] = y
            self._push("/turtle1/pose", deepcopy(self._pose))
            self._push("/odom", {"pose": deepcopy(self._pose)})
        return {
            "ok": True,
            "action": action,
            "type": action_type,
            "status": "SUCCEEDED",
            "goal": goal,
            "result": {"success": True},
        }
