"""Run: python -m backend.app.agent.time_mcp (stdio MCP server)."""
from mcp.server.fastmcp import FastMCP
from .time_tools import current_time, break_due
mcp=FastMCP('edunova-time')

@mcp.tool()
def get_current_datetime(timezone: str = 'Africa/Tunis') -> dict:
    """Give reliable current local date/time for scheduling and deadline explanations."""
    return current_time(timezone)

@mcp.tool()
def check_study_break(active_seconds: int, threshold_seconds: int = 1800) -> dict:
    """Suggest a study break after 30 minutes of actual active learning."""
    return {'break_due':break_due(active_seconds, threshold_seconds),'threshold_seconds':threshold_seconds}

if __name__=='__main__':
    mcp.run(transport='stdio')
