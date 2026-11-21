"""Privacy-aware learning analytics MCP server."""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("student-analytics")

@mcp.tool()
def get_pacing_recommendation(student_id: int) -> dict:
    """Suggest practice duration from learning activity, not a clinical diagnosis."""
    from services.analytics import pacing
    return pacing(student_id)

@mcp.tool()
def record_activity_event(student_id: int, session_id: str, event_type: str,
                          duration_seconds: int = 0) -> dict:
    """Record an explicitly authorized session activity; service enforces consent."""
    if duration_seconds < 0:
        raise ValueError("duration_seconds must be nonnegative")
    from services.analytics import log_event
    return log_event(student_id, session_id, event_type, duration_seconds)

@mcp.tool()
def get_mastery_profile(student_id: int) -> list[dict]:
    """Get accumulated learning progress and mastery."""
    from services.student import recent_progress
    return recent_progress(student_id)

if __name__ == "__main__":
    mcp.run(transport="stdio")
