import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import time

async def run_turtle_commands():
    async with stdio_client(StdioServerParameters(command='ros2-mcp')) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            await session.call_tool('publish_cmd_vel', {
                'linear_x': 0.5,
                'angular_z': 0.3
            })
            
            time.sleep(2)
            
            pose = await session.call_tool('get_pose', {})
            print(f"Pose final: {pose}")
            
            return pose

if __name__ == "__main__":
    asyncio.run(run_turtle_commands())
