"""Student memory server. Student authorization and consent are enforced in services."""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("student-memory")

@mcp.tool()
def get_student_context(student_id: int) -> dict:
    """Retrieve one authorized student's profile and learning progress."""
    from services.student import student_profile, recent_progress
    return {"profile": student_profile(student_id), "progress": recent_progress(student_id)}

@mcp.tool()
def retrieve_learning_memories(student_id: int, query: str = "", limit: int = 5) -> list[dict]:
    """Find consented educational memories associated with this student."""
    if not 1 <= limit <= 20:
        raise ValueError("limit must be between 1 and 20")
    from services.student import memory_search
    return memory_search(student_id, query, limit)

@mcp.tool()
def save_learning_observation(student_id: int, category: str, content: str) -> dict:
    """Save a learning observation only when service-layer consent permits it."""
    if len(content) > 2000:
        raise ValueError("Observation too long")
    from services.student import add_memory
    return add_memory(student_id, category, content)

if __name__ == "__main__":
    mcp.run(transport="stdio")
