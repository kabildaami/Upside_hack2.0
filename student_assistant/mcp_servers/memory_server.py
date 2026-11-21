from mcp.server.fastmcp import FastMCP
from services.student import student_profile,memory_search,add_memory,recent_progress
mcp=FastMCP('student-memory')
@mcp.tool()
def get_student_context(student_id:int)->dict:
    """Read authorized structured student information and academic progress."""
    return {'profile':student_profile(student_id),'progress':recent_progress(student_id)}
@mcp.tool()
def retrieve_learning_memories(student_id:int,query:str='',limit:int=5)->list[dict]:
    """Read consented durable learning memories; no other students."""
    return memory_search(student_id,query,limit)
@mcp.tool()
def save_learning_observation(student_id:int,category:str,content:str)->dict:
    """Propose one short educational memory; consent enforced on server."""
    return add_memory(student_id,category,content)
if __name__=='__main__':mcp.run(transport='stdio')
