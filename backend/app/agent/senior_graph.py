"""Senior LangGraph: evidence-backed coach with distinct pedagogical and cultural modes."""
from __future__ import annotations
import os
from typing import TypedDict
import httpx
from dotenv import load_dotenv
from backend.app.core.config import PROJECT_ROOT
load_dotenv(PROJECT_ROOT / '.env')
from backend.app.agent.retrieval import authorized_retrieve

class SeniorState(TypedDict, total=False):
    student_id:int
    question:str
    mode:str
    history:list[dict]
    evidence:list[dict]
    answer:str
    sources:list[dict]
    weekly_plan:list[dict]
    hobby_context:str
    status:str

def retrieve_node(state:SeniorState):
    db=state.get('_db') # injected at invocation boundary, never from request body
    chunks=authorized_retrieve(db,state['student_id'],state['question'],limit=4) if db else []
    return {'evidence':chunks,'sources':[{'document':c.get('title'),'page':c.get('page_number'),'chunk_id':c.get('chunk_id')} for c in chunks]}

SYSTEM='''You are EduNova Senior, a thoughtful, precise learning coach for pupils in grades 7-12.
Use a mature, respectful and encouraging tone: no emojis or childish gamification.
Ask the student to show reasoning, name a relevant principle, and offer one progressive hint at a time.
For ordinary conversation, respond naturally to greetings, general knowledge questions,
and explanations even when no teacher-uploaded passage covers the topic.
Do not provide the final solution to an identified active assessment. Instead use a similar
worked example, point out the next operation, or offer constructive feedback on steps.
Prefer verified teacher sources for curriculum-specific claims. General knowledge is allowed
when the sources do not cover a question; do not pretend it came from teacher material.
Never invent source citations, student XP, or assignment progress.
Encourage evidence evaluation, independent thinking, historical context and geographic literacy.
Do not claim to be a person, a best friend, a therapist, or a confidential emergency service.'''

async def _openrouter(messages):
    key=os.getenv('OPENROUTER_API_KEY','').strip()
    if not key:return None
    model=os.getenv('OPENROUTER_MODEL','openai/gpt-4o-mini')
    async with httpx.AsyncClient(timeout=35) as c:
        r=await c.post('https://openrouter.ai/api/v1/chat/completions',headers={'Authorization':f'Bearer {key}','Content-Type':'application/json','HTTP-Referer':'http://localhost:5173','X-Title':'EduNova Senior'},json={'model':model,'messages':messages,'temperature':0.35,'max_tokens':650})
        r.raise_for_status()
        return r.json()['choices'][0]['message']['content']

async def coach_node(state:SeniorState):
    sources=state.get('evidence',[])
    plan=state.get('weekly_plan',[])
    if not sources and state.get('hobby_context'):
        return {'answer':state['hobby_context'] + ' Would you like to explore one of these activities or begin a new discovery?', 'status':'hobby'}
    if not sources:
        query=state.get('question','').lower()
        if any(term in query for term in ('weekly','next week','this week','plan','goals','assignment','deadline')):
            if not plan:return {'answer':'Your teacher has not published a weekly class plan yet. You can still set personal goals in your workspace.','status':'no_plan'}
            lines=[]
            for p in plan[:4]:
                lines.append(f"{p.get('subject_name')}: {p.get('title')} ({p.get('percent',0)}% complete), {p.get('week_start')} to {p.get('week_end')}.")
                lines.extend(f" - {'Completed' if t.get('completed') else 'Pending'}: {t.get('title')}" for t in p.get('tasks',[])[:10])
            return {'answer':'Here is your verified teacher plan from EduNova:\n'+'\n'.join(lines)+'\n\nWhich pending lesson would you like to work on?', 'status':'plan'}
        # General-purpose conversation must not be blocked just because RAG
        # found no teacher-assigned chunk. Fall through to the model normally.
    context='\n\n'.join(f"SOURCE {i+1}: {c.get('title','Course')} page {c.get('page_number')}: {c['content'][:1800]}" for i,c in enumerate(sources))
    plan=state.get('weekly_plan',[])
    plan_details='\n'.join(f"Week {p.get('week_start')} to {p.get('week_end')} / {p.get('subject_name')}: " + '; '.join(f"{t.get('title')} ({'done' if t.get('completed') else 'pending'})" for t in p.get('tasks',[])) for p in plan[:4])
    messages=[{'role':'system','content':SYSTEM+'\nCURRENT TEACHER WEEKLY PLANS (only student-authorized):\n'+plan_details+'\nUse these objectives for guidance; do not invent completion or XP.\nCOURSE EVIDENCE (may be absent; general questions still deserve answers):\n'+(context or '(none)')}]
    if state.get('hobby_context'):
        messages[0]['content']+='\nHOBBY TOOL (trusted read-only student results): '+state['hobby_context']
    messages += [{'role':'user' if m.get('role')=='student' else 'assistant','content':m.get('body','')[:1500]} for m in state.get('history',[])[-8:]]
    messages.append({'role':'user','content':state['question'][:1200]})
    try: reply=await _openrouter(messages)
    except (httpx.HTTPError,KeyError,IndexError,ValueError):reply=None
    if not reply:
        reply=('Here is the relevant idea from your course: '+sources[0]['content'][:420]+'\n\nWhich first step would you take, and why?' if sources else 'The AI tutor is currently unavailable. Please try again shortly.')
    return {'answer':reply,'status':'answered'}

def route(state:SeniorState):return 'retrieve' # guided learning grounded in teacher curriculum

# Build a real LangGraph when dependencies are installed.
def build_senior_graph():
    from langgraph.graph import StateGraph,START,END
    g=StateGraph(SeniorState)
    g.add_node('retrieve',retrieve_node)
    g.add_node('coach',coach_node)
    g.add_edge(START,'retrieve');g.add_edge('retrieve','coach');g.add_edge('coach',END)
    return g.compile()

async def senior_tutor(db,student_id:int,question:str,history:list[dict],weekly_plan:list[dict]|None=None):
    # LangGraph's state must not contain database objects in a serialized checkpoint.
    # Retrieve at the trusted boundary and pass only serializable evidence through graph.
    from backend.app.agent.hobbyquest.agent_tool import latest_hobby_discovery,hobby_context_text
    hobby_context=hobby_context_text(latest_hobby_discovery(db,student_id)) if 'hobb' in question.lower() or 'interest' in question.lower() else ''
    evidence=authorized_retrieve(db,student_id,question,limit=4)
    source_refs=[{'document':x.get('title'),'page':x.get('page_number'),'chunk_id':x.get('chunk_id')} for x in evidence]
    from langgraph.graph import StateGraph,START,END
    g=StateGraph(SeniorState)
    g.add_node('coach',coach_node);g.add_edge(START,'coach');g.add_edge('coach',END)
    out=await g.compile().ainvoke({'student_id':student_id,'question':question,'history':history,'evidence':evidence,'sources':source_refs,'weekly_plan':weekly_plan or [], 'hobby_context':hobby_context})
    return {'answer':out['answer'],'sources':source_refs,'status':out['status']}
