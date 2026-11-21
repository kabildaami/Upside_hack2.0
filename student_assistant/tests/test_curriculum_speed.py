import asyncio
import time

from app.mcp_client import tool_call


async def main():
    print("Calling Curriculum MCP...")

    start = time.perf_counter()

    try:
        result = await asyncio.wait_for(
            tool_call(
                # Keep your existing tool name and arguments here
            ),
            timeout=120,
        )

        elapsed = time.perf_counter() - start

        print(f"MCP response time: {elapsed:.2f}s")
        print("Result:", result)

    except TimeoutError:
        elapsed = time.perf_counter() - start
        print(f"MCP timed out after {elapsed:.2f}s")
        raise


def test_curriculum_speed():
    asyncio.run(main())


if __name__ == "__main__":
    test_curriculum_speed()