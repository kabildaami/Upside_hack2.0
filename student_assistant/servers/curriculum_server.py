"""Grade 3 curriculum retrieval server."""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("student-curriculum")
VALID = {"Mathematics", "English", "History and geography"}

@mcp.tool()
def search_lessons(subject: str, question: str, limit: int = 4) -> list[dict]:
    """Retrieve grade-3 text with source document/page citations."""
    if subject not in VALID:
        raise ValueError(f"subject must be one of: {', '.join(sorted(VALID))}")
    if not 1 <= limit <= 12:
        raise ValueError("limit must be between 1 and 12")
    from services.rag import search_curriculum
    return search_curriculum(subject, question, limit)

@mcp.tool()
def list_course_adventures(subject: str) -> list[dict]:
    """List Maya & Leo course adventures for a valid subject."""
    if subject not in VALID:
        raise ValueError(f"subject must be one of: {', '.join(sorted(VALID))}")
    from services.rag import list_lessons
    return list_lessons(subject)

if __name__ == "__main__":
    mcp.run(transport="stdio")
