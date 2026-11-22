"""Start optional MCP server: python -m backend.app.agent.senior_mcp
Use FastMCP over stdio, no unauthenticated HTTP listener. Public readonly providers only.
"""
from __future__ import annotations
from backend.app.agent.senior_culture import wikipedia_entity_lookup,country_lookup,choose_challenge

def create_server():
    from mcp.server.fastmcp import FastMCP
    mcp=FastMCP('edunova-senior-world-knowledge')

    @mcp.tool()
    async def search_historical_entities(term:str)->list[dict]:
        """Find historical entities via Wikipedia search; source links included."""
        return await wikipedia_entity_lookup(term)

    @mcp.tool()
    async def get_country_facts(country_name:str)->list[dict]:
        """Read country facts from REST Countries (capitals, regions, population)."""
        return await country_lookup(country_name)

    @mcp.tool()
    def suggest_culture_challenge(domain:str='all')->dict:
        """Return a curated challenge prompt; teacher-controlled grading stays in FastAPI."""
        data=choose_challenge(domain)
        return {k:data[k] for k in ('key','domain','prompt','source')} if data else {'error':'No challenges'}
    return mcp

if __name__=='__main__':
    create_server().run(transport='stdio')
