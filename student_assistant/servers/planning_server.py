"""Planning and hobbies MCP server."""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("student-planning")

@mcp.tool()
def list_study_goals(student_id: int) -> list[dict]:
    """Get the student's existing learning goals."""
    from services.planning import goals
    return goals(student_id)

@mcp.tool()
def create_weekly_goal(student_id: int, subject: str, goal: str, target_date: str) -> dict:
    """Create a learning goal; target_date must be an ISO YYYY-MM-DD date."""
    from datetime import date
    date.fromisoformat(target_date)
    from services.planning import add_goal
    return add_goal(student_id, subject, goal, target_date)

@mcp.tool()
def get_hobby_catalog(student_id: int) -> list[dict]:
    """Return approved hobbies and current student interests."""
    from services.planning import hobby_catalog
    return hobby_catalog(student_id)

@mcp.tool()
def get_hobby_questions() -> list[str]:
    """Return the six questions in the student hobby survey."""
    from services.hobbies import QUESTIONS
    return QUESTIONS

@mcp.tool()
def rank_hobbies_from_six_answers(student_id: int, answers: list[str]) -> list[dict]:
    """Rank the top two hobbies with answer-by-answer evidence and scores."""
    if len(answers) != 6 or any(not a.strip() for a in answers):
        raise ValueError("Exactly six nonempty answers are required")
    from services.db import require_student
    from services.hobbies import recommend
    require_student(student_id)
    return recommend(answers, top_k=2)

if __name__ == "__main__":
    mcp.run(transport="stdio")
