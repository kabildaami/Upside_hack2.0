import asyncio
from app.mcp_client import client,tool_call
async def main():
 tools=await client().get_tools()
 print('Available MCP tools:',len(tools),*[t.name for t in tools],sep='\n - ')
 print('Clock:',await tool_call('get_current_datetime',timezone='Africa/Tunis'))
if __name__=='__main__':asyncio.run(main())
