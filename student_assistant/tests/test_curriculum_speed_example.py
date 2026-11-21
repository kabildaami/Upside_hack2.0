"""Optional live integration / latency test (requires indexed course documents)."""
import asyncio
import os
import time
import pytest
from app.mcp_client import tool_call

@pytest.mark.skipif(os.getenv("RUN_CURRICULUM_INTEGRATION") != "1",
                    reason="Enable only after RAG index and model dependencies are configured")
def test_curriculum_search_speed():
    async def run():
        start = time.perf_counter()
        result = await tool_call("search_lessons", subject="Mathematics",
                                 question="How do fractions work?", limit=2)
        assert isinstance(result, list)
        print(f"Curriculum search took {time.perf_counter() - start:.2f}s")
    asyncio.run(run())
