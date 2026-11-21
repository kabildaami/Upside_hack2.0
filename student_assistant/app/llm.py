import json,re
from openai import AsyncOpenAI
from services.config import OPENROUTER_API_KEY,OPENROUTER_MODEL

async def complete(system,user,json_mode=False):
    if not OPENROUTER_API_KEY: raise RuntimeError('OPENROUTER_API_KEY missing (LLM mode requires a real key)')
    client=AsyncOpenAI(api_key=OPENROUTER_API_KEY,base_url='https://openrouter.ai/api/v1')
    args={'model':OPENROUTER_MODEL,'temperature':0.3,'messages':[{'role':'system','content':system},{'role':'user','content':user}]}
    if json_mode:args['response_format']={'type':'json_object'}
    response=await client.chat.completions.create(**args)
    text=response.choices[0].message.content or ''
    if json_mode:
        try:return json.loads(text)
        except Exception:
            m=re.search(r'\{[\s\S]*\}',text)
            if m:return json.loads(m.group(0))
            raise
    return text
