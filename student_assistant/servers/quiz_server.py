"""Quiz MCP server: draft, present, and grade quizzes."""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("student-quiz")

@mcp.tool()
def create_quiz_draft(student_id: int, subject: str, concept: str,
                      source_chunk_id: int, question: str, options: list[str],
                      answer_index: int, hint: str = "", difficulty: int = 1) -> dict:
    """Save a draft grounded in a source chunk; teacher approval is still required."""
    if len(options) < 2 or not (0 <= answer_index < len(options)):
        raise ValueError("At least two options and a valid answer_index are required")
    if not 1 <= difficulty <= 5:
        raise ValueError("difficulty must be between 1 and 5")
    from services.quiz import create_quiz
    return create_quiz(student_id, subject, concept, source_chunk_id, question,
                       options, answer_index, hint, difficulty)

@mcp.tool()
def get_question(student_id: int, quiz_id: str) -> dict:
    """Return a student-facing question without the answer key."""
    from services.quiz import take_quiz
    result = take_quiz(student_id, quiz_id)
    # Defense in depth: never expose the stored correct answer via this tool.
    if isinstance(result, dict):
        result = {k: v for k, v in result.items() if k not in
                  {"answer_index", "correct_index", "correct_answer", "answer_key"}}
    return result

@mcp.tool()
def submit_answer(student_id: int, quiz_id: str, selected_index: int,
                  hints_used: int = 0, response_seconds: int = 0) -> dict:
    """Grade against the stored key and update mastery through the service layer."""
    if min(selected_index, hints_used, response_seconds) < 0:
        raise ValueError("indices, hints_used and response_seconds must be nonnegative")
    from services.quiz import grade
    return grade(student_id, quiz_id, selected_index, hints_used, response_seconds)

if __name__ == "__main__":
    mcp.run(transport="stdio")
