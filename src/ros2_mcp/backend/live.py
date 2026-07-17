@@ -118,7 +118,7 @@ class LiveBackend:
             "mode": "live",
             "topic": topic,
             "redacted": True,
-            "error": "live ros2 topic hz is a streaming command and is not run from MCP",
+            "error": "live ros2 topic hz is a streaming command and is not run from MCP. Use `ros2 topic hz` directly for live topic rate.",
             "note": "Capture a short CLI sample manually if needed; redact host-specific data before sharing logs.",
         }
```

This change updates the error message for the `topic_hz` method in the live backend to provide clearer guidance on how to obtain live topic rates directly using the `ros2 topic hz` command.