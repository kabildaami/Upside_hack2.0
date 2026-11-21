from mcp.server.fastmcp import FastMCP
from services.analytics import start_session,log_event,end_session,pacing
from services.student import recent_progress
mcp=FastMCP('student-analytics')
@mcp.tool()
def get_pacing_recommendation(student_id:int)->dict:
    """Suggest practice length from observed activity completion, not clinical attention diagnosis."""
    return pacing(student_id)
@mcp.tool()
def record_activity_event(student_id:int,session_id:str,event_type:str,duration_seconds:int=0)->dict:
    """Store explicit interaction timing with student consent; no webcam/keystroke monitoring."""
    return log_event(student_id,session_id,event_type,duration_seconds)
@mcp.tool()
def get_mastery_profile(student_id:int)->list[dict]:
    return recent_progress(student_id)
if __name__=='__main__':mcp.run(transport='stdio')
