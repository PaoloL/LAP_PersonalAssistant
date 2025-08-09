#!/usr/bin/env python3

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # Server parameters - adjust path as needed
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "server.py"],
        env=None
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print("Available tools:")
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")
            
            # Example: Call list_projects tool
            try:
                result = await session.call_tool("list_projects", {})
                print(f"\nProjects: {result.content}")
            except Exception as e:
                print(f"Error calling list_projects: {e}")

            # Example: Call list_issues tool
            try:
                result = await session.call_tool("list_issues_from_project", {"project_id": "AI"})
                print(f"\nIssues: {result.content}")
            except Exception as e:
                print(f"Error calling list_projects: {e}")

            # Example: call list_work_items tool
            try:
                result = await session.call_tool("list_work_items_from_issue", {"issue_id": "AI-121"})
                print(f"\nWork Items: {result.content}")
            except Exception as e:
                print(f"Error calling list_projects: {e}")

if __name__ == "__main__":
    asyncio.run(main())