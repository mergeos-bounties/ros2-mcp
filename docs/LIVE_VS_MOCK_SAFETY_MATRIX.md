# Live vs Mock Mode Safety Matrix

This document describes the safety considerations and differences between live and mock modes in ros2-mcp.

## Overview

ros2-mcp operates in two modes:

| Mode | Description | Use Case |
|------|-------------|----------|
| **Mock** | Offline, simulated data | Development, testing, demos |
| **Live** | Real ROS2 environment | Production, real robots |

## Safety Matrix

| Tool | Mock Mode | Live Mode | Safety Notes |
|------|-----------|-----------|--------------|
| `ros2_topic_list` | ✅ Returns mock topics | ⚠️ Returns real topics | Live mode may expose sensitive system info |
| `ros2_topic_echo` | ✅ Returns mock messages | 🔴 **DANGER** - Can crash robot | Never echo critical topics in production |
| `ros2_topic_publish` | ✅ Publishes to mock | 🔴 **DANGER** - Can control robot | Requires confirmation in live mode |
| `ros2_node_list` | ✅ Returns mock nodes | ⚠️ Returns real nodes | May expose internal architecture |
| `ros2_service_list` | ✅ Returns mock services | ⚠️ Returns real services | Some services are system-critical |
| `ros2_service_call` | ✅ Calls mock service | 🔴 **DANGER** - Can trigger actions | Requires confirmation in live mode |
| `ros2_action_list` | ✅ Returns mock actions | ⚠️ Returns real actions | May expose available robot actions |
| `ros2_action_goal` | ✅ Sends mock goal | 🔴 **DANGER** - Can move robot | **Never use without explicit confirmation** |
| `ros2_tf_tree` | ✅ Returns mock TF tree | ⚠️ Returns real TF tree | May expose robot configuration |
| `ros2_param_list` | ✅ Returns mock params | ⚠️ Returns real params | Some params affect robot behavior |
| `ros2_param_set` | ✅ Sets mock param | 🔴 **DANGER** - Can change robot config | Requires confirmation in live mode |

## Safety Levels

### ✅ Safe (Mock Only)
- Read-only operations
- No side effects
- Can be used freely in development

### ⚠️ Caution (Live Mode)
- Read-only but exposes real system info
- Use in controlled environments only
- Consider information disclosure

### 🔴 Danger (Live Mode)
- **Write operations** that can affect robot behavior
- **Requires explicit confirmation** from user
- **Never use in autonomous mode** without human oversight
- **Log all operations** for audit trail

## Redaction Rules

When working with live mode, sensitive information must be redacted:

### Always Redact
- API keys and tokens
- Passwords and credentials
- Private IP addresses
- Personal identifiable information (PII)
- Internal system paths

### Example Redaction

```json
{
  "topic": "/robot/cmd_vel",
  "message": {
    "linear": {"x": 0.0, "y": 0.0, "z": 0.0},
    "angular": {"x": 0.0, "y": 0.0, "z": 0.0}
  },
  "env": {
    "ROS2_MCP_MODE": "live",
    "ROS2_MCP_MASTER_URI": "<redacted>"
  }
}
```

## Best Practices

### Development (Mock Mode)
1. Use mock mode for all development work
2. Test with mock data before live deployment
3. Verify tool behavior in mock mode first

### Production (Live Mode)
1. **Always confirm** before write operations
2. **Log everything** for audit trail
3. **Use least privilege** - only enable needed tools
4. **Monitor system state** during operations
5. **Have rollback plan** for critical operations

### CI/CD
1. Use mock mode in CI pipelines
2. Never expose live credentials in CI
3. Test with mock data before production deployment

## Configuration

### Mock Mode (Default)
```json
{
  "mcpServers": {
    "ros2-mcp": {
      "command": "ros2-mcp",
      "args": ["serve"],
      "env": {
        "ROS2_MCP_MODE": "mock"
      }
    }
  }
}
```

### Live Mode
```json
{
  "mcpServers": {
    "ros2-mcp": {
      "command": "ros2-mcp",
      "args": ["serve"],
      "env": {
        "ROS2_MCP_MODE": "live",
        "ROS2_MCP_MASTER_URI": "http://localhost:11311"
      }
    }
  }
}
```

## Emergency Procedures

If a live operation causes issues:

1. **Stop immediately** - Disconnect MCP server
2. **Assess damage** - Check robot state
3. **Rollback if needed** - Restore previous configuration
4. **Document incident** - Log what happened
5. **Review process** - Update safety procedures

## References

- [MCP Host Config](MCP_HOST_CONFIG.md)
- [Cursor MCP Config](CURSOR_MCP_CONFIG.md)
- [BOUNTY.md](BOUNTY.md)
