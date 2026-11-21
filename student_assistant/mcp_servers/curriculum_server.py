
"""Curriculum MCP server for the Student Assistant.

Tools:
    search_lessons:
        Retrieve Grade 3 curriculum passages through RAG.

    list_course_adventures:
        List available course adventures.

Transport:
    stdio

Diagnostics are written to stderr to avoid interfering
with the MCP JSON-RPC protocol.
"""

import asyncio
import logging
import os
import sys
import time

from mcp.server.fastmcp import FastMCP
from services.rag import search_curriculum, list_lessons


# --------------------------------------------------
# Logging configuration
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="[CURRICULUM MCP] %(asctime)s | %(levelname)s | %(message)s",
    stream=sys.stderr,
)

logger = logging.getLogger("student-curriculum")


# --------------------------------------------------
# MCP server
# --------------------------------------------------

mcp = FastMCP("student-curriculum")

VALID_SUBJECTS = {
    "Mathematics",
    "English",
    "History and geography",
}


# --------------------------------------------------
# Tool 1: Semantic curriculum retrieval
# --------------------------------------------------


import asyncio
import logging
import time

logger = logging.getLogger("student-curriculum")

@mcp.tool()
async def search_lessons(
    subject: str,
    question: str,
    limit: int = 4,
) -> list[dict]:
    """Retrieve Grade 3 lessons with document and page citations."""

    started = time.perf_counter()

    logger.warning(
        "SEARCH_LESSONS START | subject=%s | question=%s",
        subject,
        question,
    )

    if subject not in VALID_SUBJECTS:
        return []

    try:
        logger.warning("RAG START")

        results = await asyncio.to_thread(
            search_curriculum,
            subject,
            question,
            limit,
        )

        logger.warning(
            "RAG FINISHED | %.2f seconds | %d results",
            time.perf_counter() - started,
            len(results),
        )

        return results

    except Exception:
        logger.exception("SEARCH_LESSONS FAILED")
        raise


# --------------------------------------------------
# Tool 2: List curriculum adventures
# --------------------------------------------------

@mcp.tool()
async def list_course_adventures(
    subject: str,
) -> list[dict]:
    """List the available Maya and Leo course adventures."""

    started = time.perf_counter()

    logger.info(
        "TOOL RECEIVED | list_course_adventures | subject=%s",
        subject,
    )

    if subject not in VALID_SUBJECTS:
        logger.warning("Invalid subject: %s", subject)
        return []

    try:
        results = await asyncio.to_thread(
            list_lessons,
            subject,
        )

        logger.info(
            "ADVENTURES FINISHED | duration=%.2fs | results=%d",
            time.perf_counter() - started,
            len(results),
        )

        return results

    except Exception:
        logger.exception("Failed to list course adventures")
        raise


# --------------------------------------------------
# Server startup
# --------------------------------------------------

if __name__ == "__main__":

    logger.info("Starting Student Curriculum MCP server")
    logger.info("Python executable: %s", sys.executable)
    logger.info("Working directory: %s", os.getcwd())
    logger.info(
        "DATABASE_URL configured: %s",
        bool(os.getenv("DATABASE_URL")),
    )

    # stdout is reserved for MCP protocol messages.
    mcp.run(transport="stdio")
