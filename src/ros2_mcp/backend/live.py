"""Live ROS2 backend via `ros2` CLI (no rclpy required)."""

from __future__ import annotations

import json
import shutil
import subprocess
from typing import Any

from ros2_mcp.config import domain_id, is_pub_allowed, pub_allowlist, ros2_bin


class LiveBackend:
    name = "live"

    def _run(self, args: list[str], timeout: float = 15.0) -> tuple[int, str, str]:
        bin_ = ros2_bin()
        try:
            p = subprocess.run(
                [bin_, *args],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
                env=None,  # inherit ROS_DOMAIN_ID etc.
            )
            return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()
        except FileNotFoundError:
            return 127, "", f"{bin_} not found on PATH"
        except subprocess.TimeoutExpired:
            return 124, "", "timeout"

    def doctor(self) -> dict[str, Any]:
        has = shutil.which(ros2_bin()) is not None
        code, out, err = self._run(["topic", "list"], timeout=10.0) if has else (127, "", "missing")
        return {
            "ok": has and code == 0,
            "mode": "live",
            "ros2_bin": ros2_bin(),
            "domain_id": domain_id(),
            "which": shutil.which(ros2_bin()),
            "topic_list_exit": code,
            "stdout_preview": out[:500],
            "stderr_preview": err[:500],
            "message": "live ROS2 CLI bridge" if has else "install ROS2 and source setup",
        }

    def list_topics(self) -> list[dict[str, Any]]:
        code, out, err = self._run(["topic", "list", "-t"])
        if code != 0:
            return [{"error": err or out or f"exit {code}"}]
        items: list[dict[str, Any]] = []
        for line in out.splitlines():
            line = line.strip()
            if not line:
                continue
            # format: /topic [type]
            if "[" in line and line.endswith("]"):
                name, typ = line.rsplit("[", 1)
                items.append({"name": name.strip(), "type": typ[:-1].strip()})
            else:
                items.append({"name": line, "type": ""})
        return items

    def topic_info(self, topic: str) -> dict[str, Any]:
        from ros2_mcp.backend.parsers import parse_topic_info_verbose

        code, out, err = self._run(["topic", "info", topic, "-v"])
        if code != 0:
            code2, out2, err2 = self._run(["topic", "info", topic])
            if code2 != 0:
                return {"ok": False, "error": err or err2 or out}
            return {"ok": True, "name": topic, "raw": out2, "parsed": False}
        parsed = parse_topic_info_verbose(out, topic=topic)
        parsed["parsed"] = True
        return parsed

    def topic_echo(self, topic: str, count: int = 1) -> list[dict[str, Any]]:
        n = max(1, min(count, 10))
        code, out, err = self._run(
            ["topic", "echo", topic, "--once"] if n == 1 else ["topic", "echo", topic, "--once"],
            timeout=12.0,
        )
        # ros2 topic echo --once only once; for n>1 call repeatedly
        msgs: list[dict[str, Any]] = []
        if n == 1:
            if code != 0:
                return [{"error": err or out or f"exit {code}"}]
            msgs.append({"raw": out})
            return msgs
        for _ in range(n):
            c, o, e = self._run(["topic", "echo", topic, "--once"], timeout=12.0)
            if c != 0:
                msgs.append({"error": e or o})
                break
            msgs.append({"raw": o})
        return msgs

    def topic_pub(
        self,
        topic: str,
        msg_type: str,
        data: dict[str, Any],
        times: int = 1,
    ) -> dict[str, Any]:
        if not is_pub_allowed(topic):
            return {
                "ok": False,
                "error": f"topic {topic} not in ROS2_MCP_PUB_ALLOWLIST",
                "allowlist": pub_allowlist(),
            }
        # ros2 topic pub --once <topic> <type> "<yaml/json-ish>"
        payload = json.dumps(data)
        # CLI expects YAML-like; JSON object often works for simple msgs
        args = ["topic", "pub", "--once", topic, msg_type, payload]
        if times > 1:
            args = ["topic", "pub", "-r", "10", "-t", str(min(times, 20)), topic, msg_type, payload]
        code, out, err = self._run(args, timeout=20.0)
        return {
            "ok": code == 0,
            "topic": topic,
            "type": msg_type,
            "exit": code,
            "stdout": out[:1000],
            "stderr": err[:1000],
        }

    def list_nodes(self) -> list[str]:
        from ros2_mcp.backend.parsers import parse_node_list

        code, out, err = self._run(["node", "list"])
        if code != 0:
            return [f"error: {err or out}"]
        return parse_node_list(out)

    def node_info(self, node: str) -> dict[str, Any]:
        from ros2_mcp.backend.parsers import parse_node_info

        code, out, err = self._run(["node", "info", node])
        if code != 0:
            return {"ok": False, "error": err or out}
        parsed = parse_node_info(out, node=node)
        parsed["parsed"] = True
        return parsed

    def list_services(self) -> list[dict[str, Any]]:
        from ros2_mcp.backend.parsers import parse_service_list

        code, out, err = self._run(["service", "list", "-t"])
        if code != 0:
            code2, out2, _ = self._run(["service", "list"])
            if code2 != 0:
                return [{"error": err or out}]
            return parse_service_list(out2)
        return parse_service_list(out)

    def service_call(
        self,
        service: str,
        srv_type: str,
        request: dict[str, Any],
    ) -> dict[str, Any]:
        payload = json.dumps(request)
        code, out, err = self._run(
            ["service", "call", service, srv_type, payload],
            timeout=20.0,
        )
        return {
            "ok": code == 0,
            "service": service,
            "type": srv_type,
            "stdout": out[:2000],
            "stderr": err[:1000],
        }

    def list_params(self, node: str | None = None) -> list[dict[str, Any]]:
        from ros2_mcp.backend.parsers import parse_param_list

        args = ["param", "list", node] if node else ["param", "list"]
        code, out, err = self._run(args)
        if code != 0:
            return [{"error": err or out}]
        return [
            {
                **row,
                "value": "<redacted-live-value>",
                "redacted": True,
                "note": "live mode lists parameter names only; use ros2_get_param for an explicit value read",
            }
            for row in parse_param_list(out, node=node)
        ]

    def get_param(self, node: str, name: str) -> dict[str, Any]:
        code, out, err = self._run(["param", "get", node, name])
        return {"ok": code == 0, "node": node, "name": name, "raw": out or err}

    def set_param(self, node: str, name: str, value: Any) -> dict[str, Any]:
        code, out, err = self._run(["param", "set", node, name, str(value)])
        return {"ok": code == 0, "node": node, "name": name, "value": value, "raw": out or err}

    def graph_summary(self) -> dict[str, Any]:
        topics = self.list_topics()
        nodes = self.list_nodes()
        services = self.list_services()
        return {
            "mode": "live",
            "topics": len(topics) if topics and "error" not in topics[0] else 0,
            "nodes": len(nodes) if nodes and not str(nodes[0]).startswith("error") else 0,
            "services": len(services) if services and "error" not in services[0] else 0,
            "topic_sample": topics[:20],
            "node_sample": nodes[:20],
            "doctor": self.doctor(),
        }

    def seed_demo(self) -> dict[str, Any]:
        return {
            "ok": False,
            "error": "seed_demo only applies to mock mode — start turtlesim or your bringup for live",
        }

    def tf_tree(self) -> dict[str, Any]:
        code, out, err = self._run(["run", "tf2_tools", "view_frames"], timeout=5.0)
        # Prefer topic echo of /tf once as structured-ish dump
        c2, o2, e2 = self._run(["topic", "echo", "/tf", "--once"], timeout=8.0)
        return {
            "mode": "live",
            "ok": c2 == 0 or code == 0,
            "tf_echo": (o2 or e2)[:2000],
            "view_frames_note": "install tf2_tools for full PDF tree; echo /tf shown when available",
            "stderr": (err or e2)[:500],
        }

    def bag_info(self, path: str | None = None) -> dict[str, Any]:
        if not path:
            return {"ok": False, "mode": "live", "error": "path is required for live ros2 bag info"}
        from ros2_mcp.backend.parsers import parse_bag_info

        code, out, err = self._run(["bag", "info", path], timeout=20.0)
        if code != 0:
            return {
                "ok": False,
                "mode": "live",
                "path": path,
                "exit": code,
                "stderr": err[:1000],
                "stdout": out[:1000],
            }
        parsed = parse_bag_info(out)
        parsed.update({"mode": "live", "path": parsed.get("path") or path, "raw": out[:4000]})
        return parsed

    def list_actions(self) -> list[dict[str, Any]]:
        code, out, err = self._run(["action", "list", "-t"])
        if code != 0:
            code2, out2, err2 = self._run(["action", "list"])
            if code2 != 0:
                return [{"error": err or err2 or out or "ros2 action list failed"}]
            return [{"name": ln.strip(), "type": ""} for ln in out2.splitlines() if ln.strip()]
        items: list[dict[str, Any]] = []
        for line in out.splitlines():
            line = line.strip()
            if not line:
                continue
            if "[" in line and line.endswith("]"):
                name, typ = line.rsplit("[", 1)
                items.append({"name": name.strip(), "type": typ[:-1].strip()})
            else:
                items.append({"name": line, "type": ""})
        return items

    def action_send_goal(
        self,
        action: str,
        action_type: str,
        goal: dict[str, Any],
    ) -> dict[str, Any]:
        payload = json.dumps(goal)
        code, out, err = self._run(
            ["action", "send_goal", action, action_type, payload],
            timeout=30.0,
        )
        return {
            "ok": code == 0,
            "action": action,
            "type": action_type,
            "stdout": out[:2000],
            "stderr": err[:1000],
        }
