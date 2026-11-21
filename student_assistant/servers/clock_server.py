"""Local clock MCP server."""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("student-clock")

@mcp.tool()
def get_current_datetime(timezone: str = "Africa/Tunis") -> dict:
    """Get real local time, weekday and next-week bounds."""
    from services.planning import clock
    return clock(timezone)

if __name__ == "__main__":
    mcp.run(transport="stdio")
