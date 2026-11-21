from mcp.server.fastmcp import FastMCP
from services.planning import clock,goals,add_goal,hobby_catalog
from services.hobbies import recommend,QUESTIONS
mcp=FastMCP('student-planning')
@mcp.tool()
def list_study_goals(student_id:int)->list[dict]:
    return goals(student_id)
@mcp.tool()
def create_weekly_goal(student_id:int,subject:str,goal:str,target_date:str)->dict:
    """Save a short learning goal with a specific date; date obtained from clock tool."""
    return add_goal(student_id,subject,goal,target_date)
@mcp.tool()
def get_hobby_catalog(student_id:int)->list[dict]:
    """Get the platform's approved hobby catalog and selected interests."""
    return hobby_catalog(student_id)
@mcp.tool()
def get_hobby_questions()->list[str]:
    """Six user-facing questions for a traceable hobby questionnaire."""
    return QUESTIONS
@mcp.tool()
def rank_hobbies_from_six_answers(student_id:int,answers:list[str])->list[dict]:
    """Return top 2 scored hobbies, explaining which answer numbers contributed."""
    from services.db import require_student
    require_student(student_id)
    return recommend(answers,top_k=2)
if __name__=='__main__':mcp.run(transport='stdio')
