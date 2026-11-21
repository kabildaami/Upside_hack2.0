"""Bounded LangGraph learning workflow. All student records restricted to incoming student_id.
For actual deployment student_id MUST be derived from verified auth, never from LLM.
"""
import json,re
from statistics import mode
from typing import TypedDict
from langgraph.graph import StateGraph,START,END
from services.student import student_profile,consented,recent_progress,memory_search,recent_thread
from services.db import query
from app.llm import complete
from app.mcp_client import tool_call

SUBJECTS={'math':'Mathematics','maths':'Mathematics','number':'Mathematics','english':'English','reading':'English','story':'English','history':'History and geography','geography':'History and geography','map':'History and geography'}
class State(TypedDict,total=False):
    student_id:int
    thread_id:str
    message:str
    mode:str
    subject:str
    profile:dict
    memories:list
    progress:list
    time:dict
    pacing:dict
    evidence:list
    response:str
    quiz_id:str
    action:str
    recent_turns:list

def detect_mode(message):
    t=message.lower()
    if re.fullmatch(r'\s*[1-4]\s*',t):return 'answer'
    if re.search(r'\b(quiz|test me|questions|practice)\b',t):return 'quiz'
    if re.search(r'\b(next week|plan|schedule|goal|tomorrow)\b',t):return 'plan'
    if re.search(r'\b(hobby|hobbies|interests|activity ideas)\b',t) or re.search(r'(?m)^\s*6[\).:-]',t):return 'hobby'
    return 'tutor'

def detect_subject(message):
    t=message.lower()
    for key,subject in SUBJECTS.items():
        if key in t:return subject
    return 'Mathematics'

async def load_context(state:State):
    profile=student_profile(state['student_id'])
    if not profile:raise ValueError('Student not found')
    if not state.get('thread_id'):raise ValueError('thread_id required')
    sid=state['student_id'];message=state.get('message','')[:2500]
    # Date/time comes from a real MCP clock service.
    date=await tool_call('get_current_datetime',timezone=profile.get('timezone') or 'Africa/Tunis')
    try:pacing=await tool_call('get_pacing_recommendation',student_id=sid)
    except Exception:pacing={'activity_minutes':12}
    return {'profile':profile,'memories':memory_search(sid,limit=6),'progress':recent_progress(sid,8),
            'time':date,'pacing':pacing,'recent_turns':recent_thread(sid,state['thread_id']), 'mode':detect_mode(message),'subject':detect_subject(message)}

async def retrieve(state: State):
    mode = state.get("mode") or detect_mode(
        state.get("message", "")
    )

    if mode == "answer":
        return {"evidence": []}
    if mode == 'hobby':
        return {'evidence':[await tool_call('get_hobby_catalog',student_id=state['student_id'])]}
    if state['mode']=='plan':
        return {'evidence':[await tool_call('list_study_goals',student_id=state['student_id'])]}
    # For the initial Grade 3 corpus, lessons for older students are NOT represented as grade-appropriate.
    if state['profile'].get('age_variant')=='senior' or (state['profile'].get('grade_level') not in (None,'3rd primary')):
        return {'evidence':[]}
    chunks=await tool_call('search_lessons',subject=state['subject'],question=state['message'],limit=4)
    return {'evidence':chunks if isinstance(chunks,list) else [chunks]}

async def respond(state:State):
    mode=state['mode']; profile=state['profile']; sid=state['student_id']
    junior=profile.get('age_variant')!='senior'
    allowed_context=(not junior or profile.get('grade_level') in (None,'3rd primary'))
    source_context=json.dumps(state.get('evidence',[]),default=str)[:12000]
    shared=('You are a transparent AI educational assistant, never a human friend. '
            'Avoid emotionally dependent framing; never ask for personal secrets. '
            'Student interests and school preferences are not medical diagnoses. '
            'Do not fabricate course facts or references. If course material is missing, say so. '
            'Always provide source filename and page for source-grounded facts. '
            'Never claim a quiz was graded or saved unless tools confirm it. '
            'Keep all content age-appropriate and respectful.')
    pedagogy=('For ages 6-12: warm, concise storytelling with a single small activity and optional break. '
              if junior else 'For ages 13-18: focused Socratic tutoring; hint first, ask learner to attempt a step, do not immediately give final math solution. ')
    prompt=(shared+pedagogy+
            f' Current mode: {mode}. Student context (use minimal information): '
            f'{json.dumps({"first_name":profile.get("first_name"),"grade":profile.get("grade_level"),"progress":state.get("progress",[]),"memories":state.get("memories",[]),"pacing":state.get("pacing"),"recent_turns":state.get("recent_turns",[]),"interests":profile.get("interests"),"difficult_subjects":profile.get("difficult_subjects"),"difficulty_level":profile.get("difficulty_level"),"help_wanted":profile.get("help_wanted")},default=str)[:5500]}. '
            'Teacher course evidence: '+source_context)
    if not allowed_context and mode in ('quiz','tutor'):
        return {'response':'I only have Grade 3 English, Maths and History/Geography materials right now. Ask your teacher to upload curriculum for your grade; I can still help you organize a study plan.','action':'unsupported_grade'}
    if mode=='hobby':
        import re
        answers=re.findall(r'(?m)^\s*[1-6][\).:-]\s*(.+)$',state['message'])
        if len(answers)==6:
            ranked=await tool_call('rank_hobbies_from_six_answers',student_id=sid,answers=answers)
            return {'response':json.dumps({'recommendations':ranked},ensure_ascii=False,default=str),'action':'hobby_recommendations'}
        questions=await tool_call('get_hobby_questions')
        if not isinstance(questions,list):questions=[]
        return {'response':'Answer these six questions on separate numbered lines:\n'+'\n'.join(f'{i+1}. {q}' for i,q in enumerate(questions)),'action':'hobby_questions'}
    if mode=='answer':
        latest=query('''SELECT q.id FROM assistant.quiz_items q
          LEFT JOIN assistant.quiz_attempts a ON a.quiz_item_id=q.id AND a.student_id=%s
          WHERE q.student_id=%s AND a.id IS NULL ORDER BY q.created_at DESC LIMIT 1''',(sid,sid),fetch='one')
        if not latest:return {'response':'There is no unanswered quiz yet. Ask me to make a quiz!','action':'no_active_quiz'}
        graded=await tool_call('submit_answer',student_id=sid,quiz_id=str(latest['id']),selected_index=int(state['message'])-1,hints_used=0,response_seconds=0)
        if isinstance(graded,dict) and graded.get('is_correct') is not None:
            return {'response':('Correct! Nice reasoning.' if graded['is_correct'] else 'Not quite. Let us revisit the key idea together.'),'action':'quiz_graded'}
        return {'response':'I could not verify this attempt. Please retry.','action':'grading_error'}
    if mode=='quiz':
        # Create a question draft with a source-linked answer key; keep answer hidden from student.
        # A human must review model-generated quizzes before official/classroom use.
        chunks=state.get('evidence',[])
        if not chunks:return {'response':'I could not find an approved lesson for that quiz. Try specifying a topic from the course.','action':'no_evidence'}
        data=await complete(prompt+' Return JSON with keys: concept,question,options (exactly 4 strings),answer_index (0-3),hint,difficulty (1-5). Ground the answer in evidence; never invent citations.',state['message'],json_mode=True)
        if not isinstance(data,dict) or not isinstance(data.get('options'),list) or len(data['options'])!=4 or not 0<=int(data.get('answer_index',-1))<4:
            return {'response':'I could not validate this quiz draft; please try a narrower topic.','action':'invalid_quiz'}
        first=chunks[0]
        if not isinstance(first,dict) or 'id' not in first:return {'response':'Missing course source for the quiz.','action':'no_source'}
        saved=await tool_call('create_quiz_draft',student_id=sid,subject=state['subject'],concept=str(data.get('concept') or state['subject'])[:120],source_chunk_id=int(first['id']),question=str(data['question']),options=[str(x) for x in data['options']],answer_index=int(data['answer_index']),hint=str(data.get('hint','')),difficulty=min(5,max(1,int(data.get('difficulty',1)))))
        qid=saved.get('id') if isinstance(saved,dict) else None
        question=str(data['question'])+'\n'+'\n'.join(f'{i+1}. {opt}' for i,opt in enumerate(data['options']))
        return {'response':question+'\n(Answer using a number from 1 to 4.)','quiz_id':str(qid or ''),'action':'quiz_draft_created'}
    if mode=='plan':
        from datetime import date,timedelta
        dates=state.get('time') or {}
        preview_only=not any(w in state['message'].lower() for w in ('save','set my','create goals','add goals'))
        guide=await complete(prompt+' Produce exactly 3 realistic short goals with planned weekday. Return JSON with goals list, each having subject, goal, weekday (0=Mon to 6=Sun). Use next week based on clock; avoid overscheduling.',
            f'Clock: {dates}. Request: {state["message"]}',json_mode=True)
        monday=date.fromisoformat(dates['next_week_monday'])
        possible=guide.get('goals',[]) if isinstance(guide,dict) else []
        out=[]
        for item in possible[:3]:
            if not isinstance(item,dict):continue
            day=max(0,min(6,int(item.get('weekday',0))))
            goal=str(item.get('goal',''))[:180]
            subj=str(item.get('subject','Mathematics'))[:70]
            if not goal:continue
            row={'date':(monday+timedelta(days=day)).isoformat(),'subject':subj,'goal':goal}
            if not preview_only:
                row['save_result']=await tool_call('create_weekly_goal',student_id=sid,subject=subj,goal=goal,target_date=row['date'])
            out.append(row)
        return {'response':json.dumps({'goals':out,'status':'preview_only' if preview_only else 'save_attempted'},default=str,ensure_ascii=False),'action':'plan_preview' if preview_only else 'plan_saved'}
    answer=await complete(prompt,state['message'])
    return {'response':answer,'action':mode}

async def persist(state:State):
    from services.student import consented
    # Conversation retention is opt-in; academic outcomes are kept as structured records separately.
    if consented(state['student_id'],'learning_memory'):
        query('''INSERT INTO assistant.conversation_turns(student_id,thread_id,role,message)
          VALUES(%s,%s,'student',%s),(%s,%s,'assistant',%s)''',
          (state['student_id'],state['thread_id'],state['message'][:2500],state['student_id'],state['thread_id'],state.get('response','')[:6000]),fetch='none')
    # Only explicitly stated explanation preferences are candidates for durable memory.
    msg=state.get('message','').lower()
    if consented(state['student_id'],'learning_memory') and any(x in msg for x in ('i prefer visual','i prefer examples','please use pictures','i learn better with')):
        from services.student import add_memory
        try:
            existing=memory_search(state['student_id'],limit=20)
            preference=state['message'][:250]
            if not any(x['content'].lower()==preference.lower() for x in existing):
                add_memory(state['student_id'],'learning_preference',preference)
        except Exception: pass
    return {}

def route(state:State):return 'retrieve'

def build_graph(checkpointer=None):
    b=StateGraph(State)
    b.add_node('student_context',load_context)
    b.add_node('retrieve_tools',retrieve)
    b.add_node('educational_response',respond)
    b.add_node('persist_context',persist)
    b.add_edge(START,'student_context');b.add_edge('student_context','retrieve_tools');b.add_edge('retrieve_tools','educational_response');b.add_edge('educational_response','persist_context');b.add_edge('persist_context',END)
    return b.compile(checkpointer=checkpointer)

graph=build_graph()  # Studio owns its checkpoint lifecycle; CLI sets a Postgres checkpointer separately.
