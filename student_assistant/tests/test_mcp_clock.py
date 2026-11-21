"""Real transport integration test with a low-cost tool."""
import asyncio
from app.mcp_client import tool_call

def test_clock_mcp_call():
    result = asyncio.run(tool_call("get_current_datetime", timezone="Africa/Tunis"))
    assert isinstance(result, dict)
    assert result
