from mcp.server.fastmcp import FastMCP
from services.quiz import create_quiz,take_quiz,grade
mcp=FastMCP('student-quiz')
@mcp.tool()
def create_quiz_draft(student_id:int,subject:str,concept:str,source_chunk_id:int,question:str,options:list[str],answer_index:int,hint:str='',difficulty:int=1)->dict:
    """Save a structurally valid DRAFT quiz grounded in a course chunk; teacher review still needed."""
    return create_quiz(student_id,subject,concept,source_chunk_id,question,options,answer_index,hint,difficulty)
@mcp.tool()
def get_question(student_id:int,quiz_id:str)->dict:
    """Get student-facing question without its correct answer."""
    return take_quiz(student_id,quiz_id)
@mcp.tool()
def submit_answer(student_id:int,quiz_id:str,selected_index:int,hints_used:int=0,response_seconds:int=0)->dict:
    """Grade using stored answer key, update mastery atomically."""
    return grade(student_id,quiz_id,selected_index,hints_used,response_seconds)
if __name__=='__main__':mcp.run(transport='stdio')
