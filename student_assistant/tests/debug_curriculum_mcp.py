
import asyncio
import time
import traceback

from app.mcp_client import tool_call


async def main():
    print("Starting Curriculum MCP test...", flush=True)
    start = time.perf_counter()

    try:
        result = await asyncio.wait_for(
            tool_call(
                "search_lessons",
                subject="Mathematics",
                question="place value tens hundreds",
                limit=2,
            ),
            timeout=120,
        )

        print(
            f"SUCCESS in {time.perf_counter() - start:.2f}s",
            flush=True,
        )
        print(str(result)[:2000])

    except Exception:
        print(
            f"FAILED after {time.perf_counter() - start:.2f}s",
            flush=True,
        )
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
