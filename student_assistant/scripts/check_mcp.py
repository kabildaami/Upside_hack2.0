"""Run with python -m scripts.check_mcp from project root."""
import asyncio
import json
from app.mcp_client import list_mcp_tools, tool_call

async def main():
    print("Discovering registered MCP tools...", flush=True)
    catalog = await list_mcp_tools()
    print(json.dumps(catalog, indent=2))
    print("\nCalling the clock tool...", flush=True)
    result = await tool_call("get_current_datetime", timezone="Africa/Tunis")
    print(json.dumps(result, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(main())
