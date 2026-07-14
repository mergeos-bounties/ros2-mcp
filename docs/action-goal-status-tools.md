import { z } from "zod";
import { McpError, ErrorCode } from "@modelcontextprotocol/sdk/types.js";
import { MockROS2Backend } from "../mock/backend.js";

const SendActionGoalArgsSchema = z.object({
  action_name: z.string().describe("Name of the action to call"),
  action_type: z.string().describe("Type of the action"),
  goal: z.record(z.any()).describe("Goal message as JSON object"),
});

const GetActionStatusArgsSchema = z.object({
  goal_id: z.string().describe("UUID of the action goal to check status for"),
});

const CancelActionGoalArgsSchema = z.object({
  goal_id: z.string().describe("UUID of the action goal to cancel"),
});

export async function handleSendActionGoal(
  backend: MockROS2Backend,
  args: unknown
): Promise<{ content: Array<{ type: string; text: string }> }> {
  const parsed = SendActionGoalArgsSchema.parse(args);
  const { action_name, action_type, goal } = parsed;

  const result = backend.sendActionGoal(action_name, action_type, goal);

  return {
    content: [
      {
        type: "text",
        text: JSON.stringify(result, null, 2),
      },
    ],
  };
}

export async function handleGetActionStatus(
  backend: MockROS2Backend,
  args: unknown
): Promise<{ content: Array<{ type: string; text: string }> }> {
  const parsed = GetActionStatusArgsSchema.parse(args);
  const { goal_id } = parsed;

  const result = backend.getActionStatus(goal_id);

  if (!result) {
    throw new McpError(
      ErrorCode.InvalidRequest,
      `Action goal with ID ${goal_id} not found`
    );
  }

  return {
    content: [
      {
        type: "text",
        text: JSON.stringify(result, null, 2),
      },
    ],
  };
}

export async function handleCancelActionGoal(
  backend: MockROS2Backend,
  args: unknown
): Promise<{ content: Array<{ type: string; text: string }> }> {
  const parsed = CancelActionGoalArgsSchema.parse(args);
  const { goal_id } = parsed;

  const result = backend.cancelActionGoal(goal_id);

  return {
    content: [
      {
        type: "text",
        text: JSON.stringify(result, null, 2),
      },
    ],
  };
}

export const actionToolDefinitions = [
  {
    name: "ros2_send_action_goal",
    description:
      "Send a goal to a ROS2 action server and receive a goal ID for tracking",
    inputSchema: {
      type: "object",
      properties: {
        action_name: {
          type: "string",
          description: "Name of the action to call",
        },
        action_type: {
          type: "string",
          description: "Type of the action (e.g., example_interfaces/action/Fibonacci)",
        },
        goal: {
          type: "object",
          description: "Goal message as JSON object",
        },
      },
      required: ["action_name", "action_type", "goal"],
    },
  },
  {
    name: "ros2_get_action_status",
    description: "Get the status and result of a previously sent action goal",
    inputSchema: {
      type: "object",
      properties: {
        goal_id: {
          type: "string",
          description: "UUID of the action goal to check status for",
        },
      },
      required: ["goal_id"],
    },
  },
  {
    name: "ros2_cancel_action_goal",
    description: "Cancel a previously sent action goal",
    inputSchema: {
      type: "object",
      properties: {
        goal_id: {
          type: "string",
          description: "UUID of the action goal to cancel",
        },
      },
      required: ["goal_id"],
    },
  },
];