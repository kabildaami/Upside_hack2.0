
import asyncio
import time
import pytest

from app.mcp_client import tool_call


@pytest.mark.parametrize(
    "tool_name,arguments",
    [
        ("get_current_datetime", {"timezone": "Africa/Tunis"}),
        (
            "search_lessons",
            {
                "subject": "Mathematics",
                "question": "place value",
                "limit": 2,
            },
        ),
    ],
)
def test_mcp_connection(tool_name, arguments):
    async def execute():
        return await asyncio.wait_for(
            tool_call(tool_name, **arguments),
            timeout=90,
        )

    start = time.perf_counter()

    result = asyncio.run(execute())

    elapsed = time.perf_counter() - start

    print(f"\nTool: {tool_name}")
    print(f"Duration: {elapsed:.2f} seconds")
    print(f"Result: {str(result)[:1000]}")

    assert result is not None
