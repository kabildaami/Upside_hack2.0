from mcp.server.fastmcp import FastMCP
from services.planning import clock
mcp=FastMCP('student-clock')
@mcp.tool()
def get_current_datetime(timezone: str='Africa/Tunis') -> dict:
    """Return actual local date/time, weekday and next week's boundaries from system clock."""
    return clock(timezone)
if __name__=='__main__':mcp.run(transport='stdio')
