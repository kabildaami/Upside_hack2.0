"""Grade 7-12 rigorous step quizzes. Teacher approves; server awards idempotent XP."""
import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.tables import User
from backend.app.security.dependencies import roles_allowed
from backend.app.api.curriculum import owner
from backend.app.api.student_experience import student_context
from backend.app.agent.reasoning_grader import source_match, verify_step, quiz_safe_summary

router=APIRouter(prefix='/reasoning',tags=['Senior step-by-step mathematics'])

class PackImport(BaseModel):
    document_id:int
    questions:list[dict]=Field(min_length=1,max_length=50)

class StudentAttempt(BaseModel):
    response:str=Field(min_length=1,max_length=200)
    reasoning:str=Field(min_length=12,max_length=2000)


def senior_sid(db,user):
    row,grade=student_context(db,user)
    if not 7<=grade<=12:raise HTTPException(403,'Senior mathematics only')
    return row['student_id']

@router.post('/teacher/import',status_code=201)
def teacher_import(payload:PackImport,db:Session=Depends(get_db),user:User=Depends(roles_allowed('teacher'))):
    doc=owner(db,payload.document_id,user.user_id)
    if not doc:raise HTTPException(403,'Document not assigned to you')
    metadata=db.execute(text('''SELECT d.school_id,d.class_id,d.subject_id,d.teacher_id,c.grade_level,s.subject_name
      FROM public.teacher_curriculum_documents d JOIN public.classes c ON c.class_id=d.class_id
      JOIN public.subjects s ON s.subject_id=d.subject_id WHERE d.id=:id AND d.status='ready' '''),{'id':payload.document_id}).mappings().first()
    if not metadata:raise HTTPException(422,'Document must finish processing first')
    if 'math' not in metadata['subject_name'].lower():raise HTTPException(422,'Please choose a mathematics curriculum')
    # Validate all questions and lesson-specific source links before the first insert.
    chunks=[dict(x) for x in db.execute(text('SELECT id,content FROM public.teacher_curriculum_chunks WHERE document_id=:doc ORDER BY chunk_index'),{'doc':payload.document_id}).mappings()]
    prepared=[]
    for q in payload.questions:
        steps=q.get('steps',[])
        if not isinstance(steps,list) or not 2<=len(steps)<=12:raise HTTPException(422,'Each quiz needs 2-12 ordered reasoning steps')
        if any(s.get('check_type') not in ('exact','numeric') or not s.get('expected_answer') or not s.get('prompt') or not s.get('hint') or not 0<=int(s.get('xp',-1))<=30 for s in steps):
            raise HTTPException(422,'Each step needs a prompt, answer, hint, check type and XP')
        match=next((chunk for chunk in chunks if source_match(chunk['content'],q.get('lesson_key',''),q.get('source_terms',[]))),None)
        if match is None:raise HTTPException(422,f"No matching curriculum chunk for {q.get('lesson_key','unknown')}; upload the matching Grade 11 program first")
        prepared.append((q,match['id']))
    created=[]
    try:
        for q,chunk_id in prepared:
            # A repeated import produces a clean 409 rather than overwriting teacher-reviewed items.
            existing=db.execute(text('SELECT 1 FROM public.senior_reasoning_quizzes WHERE document_id=:doc AND lesson_key=:key AND title=:title'),{'doc':payload.document_id,'key':q['lesson_key'],'title':q['title']}).scalar()
            if existing:raise HTTPException(409,f"Quiz already imported: {q['title']}")
            qid=db.execute(text('''INSERT INTO public.senior_reasoning_quizzes(school_id,class_id,document_id,source_chunk_id,teacher_id,subject_id,lesson_key,title,statement,teacher_explanation)
             VALUES (:school,:class_id,:doc,:chunk,:teacher,:subject,:key,:title,:statement,:exp) RETURNING id'''),{'school':metadata['school_id'],'class_id':metadata['class_id'],'doc':payload.document_id,'chunk':chunk_id,'teacher':metadata['teacher_id'],'subject':metadata['subject_id'],'key':q['lesson_key'],'title':q['title'],'statement':q['statement'],'exp':q.get('teacher_explanation','')}).scalar_one()
            for pos,s in enumerate(q['steps'],1):
                db.execute(text('''INSERT INTO public.senior_reasoning_steps(quiz_id,position,prompt,expected_answer,check_type,hint,xp)
                 VALUES (:qid,:pos,:prompt,:answer,:kind,:hint,:xp)'''),{'qid':qid,'pos':pos,'prompt':s['prompt'],'answer':str(s['expected_answer']),'kind':s['check_type'],'hint':s['hint'],'xp':s['xp']})
            created.append(qid)
        db.commit()
    except Exception:
        db.rollback();raise
    return {'imported_ids':created,'status':'draft','required_action':'Teacher review and approval'}

@router.get('/teacher/quizzes')
def teacher_quizzes(document_id:int,db:Session=Depends(get_db),user:User=Depends(roles_allowed('teacher'))):
    if not owner(db,document_id,user.user_id):raise HTTPException(404,'Document unavailable')
    quizzes=[dict(r) for r in db.execute(text('''SELECT id,title,statement,lesson_key,status,source_chunk_id,teacher_explanation
      FROM public.senior_reasoning_quizzes WHERE document_id=:doc ORDER BY id DESC'''),{'doc':document_id}).mappings()]
    for q in quizzes:
        q['steps']=[dict(s) for s in db.execute(text('SELECT id,position,prompt,expected_answer,check_type,hint,xp FROM public.senior_reasoning_steps WHERE quiz_id=:id ORDER BY position'),{'id':q['id']}).mappings()]
    return quizzes

@router.post('/teacher/quizzes/{quiz_id}/approve')
def approve(quiz_id:int,db:Session=Depends(get_db),user:User=Depends(roles_allowed('teacher'))):
    qid=db.execute(text('''UPDATE public.senior_reasoning_quizzes q SET status='approved'
      FROM public.teachers t WHERE q.id=:id AND q.teacher_id=t.teacher_id AND t.user_id=:uid RETURNING q.id'''),{'id':quiz_id,'uid':user.user_id}).scalar_one_or_none()
    if not qid:raise HTTPException(404,'Quiz unavailable')
    db.commit();return {'approved':True,'id':qid}

@router.get('/student/quizzes')
def student_quizzes(db:Session=Depends(get_db),user:User=Depends(roles_allowed('student'))):
    sid=senior_sid(db,user)
    quiz_rows=[dict(q) for q in db.execute(text('''SELECT DISTINCT q.id,q.title,q.statement,q.lesson_key
      FROM public.senior_reasoning_quizzes q
      JOIN public.teacher_curriculum_documents d ON d.id=q.document_id AND d.status='ready'
      JOIN public.student_enrollments e ON e.class_id=q.class_id AND e.school_id=q.school_id AND e.ended_at IS NULL
      JOIN public.teacher_classes tc ON tc.class_id=q.class_id AND tc.school_id=q.school_id AND tc.teacher_id=q.teacher_id AND tc.subject_id=q.subject_id
      WHERE e.student_id=:sid AND q.status='approved' ORDER BY q.id DESC LIMIT 70'''),{'sid':sid}).mappings()]
    return [_load_quiz(db,q,sid) for q in quiz_rows]


def _load_quiz(db,q,sid):
    steps=[dict(s) for s in db.execute(text('SELECT id,position,prompt,xp FROM public.senior_reasoning_steps WHERE quiz_id=:qid ORDER BY position'),{'qid':q['id']}).mappings()]
    completed={s['position'] for s in db.execute(text('''SELECT DISTINCT st.position FROM public.senior_reasoning_steps st
       JOIN public.senior_step_xp xp ON xp.step_id=st.id AND xp.student_id=:sid WHERE st.quiz_id=:qid'''),{'qid':q['id'],'sid':sid}).mappings()}
    return quiz_safe_summary(q,steps,completed)

@router.get('/student/quizzes/{quiz_id}/hint')
def hint(quiz_id:int,db:Session=Depends(get_db),user:User=Depends(roles_allowed('student'))):
    sid=senior_sid(db,user)
    q=_permitted(db,quiz_id,sid)
    data=_load_quiz(db,q,sid)
    next_step=data['next_step']
    if not next_step:raise HTTPException(409,'Already completed')
    value=db.execute(text('SELECT hint FROM public.senior_reasoning_steps WHERE id=:id'),{'id':next_step['id']}).scalar_one()
    return {'step_id':next_step['id'],'hint':value}


def _permitted(db,quiz_id,sid):
    q=db.execute(text('''SELECT DISTINCT q.id,q.title,q.statement,q.lesson_key
      FROM public.senior_reasoning_quizzes q
      JOIN public.teacher_curriculum_documents d ON d.id=q.document_id AND d.status='ready'
      JOIN public.student_enrollments e ON e.class_id=q.class_id AND e.school_id=q.school_id AND e.ended_at IS NULL
      JOIN public.teacher_classes tc ON tc.class_id=q.class_id AND tc.school_id=q.school_id AND tc.teacher_id=q.teacher_id AND tc.subject_id=q.subject_id
      WHERE q.id=:id AND e.student_id=:sid AND q.status='approved' '''),{'id':quiz_id,'sid':sid}).mappings().first()
    if not q:raise HTTPException(404,'Quiz unavailable for your class')
    return dict(q)

@router.post('/student/quizzes/{quiz_id}/answer')
def answer(quiz_id:int,payload:StudentAttempt,db:Session=Depends(get_db),user:User=Depends(roles_allowed('student'))):
    sid=senior_sid(db,user)
    # One transaction serializes the active student/quiz reward decision.
    db.execute(text('SELECT student_id FROM public.students WHERE student_id=:sid FOR UPDATE'),{'sid':sid})
    q=_permitted(db,quiz_id,sid);summary=_load_quiz(db,q,sid)
    step=summary['next_step']
    if not step:return {'correct':True,'xp_awarded':0,'feedback':'Already completed','quiz':summary}
    private=db.execute(text('SELECT expected_answer,check_type,xp FROM public.senior_reasoning_steps WHERE id=:id'),{'id':step['id']}).mappings().one()
    correct=verify_step(payload.response,private['expected_answer'],private['check_type'])
    db.execute(text('INSERT INTO public.senior_reasoning_attempts(student_id,step_id,response_text,reasoning_text,is_correct) VALUES (:sid,:id,:response,:reasoning,:correct)'),{'sid':sid,'id':step['id'],'response':payload.response,'reasoning':payload.reasoning,'correct':correct})
    gained=0
    if correct:
        gained=db.execute(text('''INSERT INTO public.senior_step_xp(student_id,step_id,points) VALUES (:sid,:id,:xp)
           ON CONFLICT(student_id,step_id) DO NOTHING RETURNING points'''),{'sid':sid,'id':step['id'],'xp':private['xp']}).scalar_one_or_none() or 0
    if correct and not _load_quiz(db,q,sid)['next_step']:
        # Credit only fully solved quizzes against a teacher's published weekly quiz target.
        tasks=db.execute(text('''SELECT task.id,task.target_correct,task.xp_reward
          FROM public.edunova_plan_tasks task
          JOIN public.edunova_weekly_plans p ON p.id=task.plan_id AND p.published=true
          JOIN public.senior_reasoning_quizzes rq ON rq.id=:quiz AND rq.class_id=p.class_id AND rq.subject_id=p.subject_id AND rq.school_id=p.school_id
          WHERE task.kind='quiz' AND task.lesson_key=rq.lesson_key AND p.week_end>=CURRENT_DATE - 7'''),{'quiz':quiz_id}).mappings().all()
        for task in tasks:
            credited=db.execute(text('''INSERT INTO public.senior_reasoning_quiz_credit(student_id,quiz_id,task_id)
              VALUES (:sid,:quiz,:task) ON CONFLICT DO NOTHING RETURNING quiz_id'''),{'sid':sid,'quiz':quiz_id,'task':task['id']}).scalar_one_or_none()
            if credited is None:continue
            db.execute(text('''INSERT INTO public.edunova_student_task_progress(student_id,task_id,correct_count)
              VALUES (:sid,:task,1) ON CONFLICT(student_id,task_id)
              DO UPDATE SET correct_count=public.edunova_student_task_progress.correct_count+1'''),{'sid':sid,'task':task['id']})
            db.execute(text('''UPDATE public.edunova_student_task_progress SET completed_at=now()
              WHERE student_id=:sid AND task_id=:task AND correct_count>=:target AND completed_at IS NULL'''),{'sid':sid,'task':task['id'],'target':task['target_correct']})
            done=db.execute(text('SELECT completed_at IS NOT NULL FROM public.edunova_student_task_progress WHERE student_id=:sid AND task_id=:task'),{'sid':sid,'task':task['id']}).scalar_one()
            if done:
                db.execute(text('''INSERT INTO public.edunova_xp_events(student_id,task_id,points,reason)
                  VALUES (:sid,:task,:xp,'senior weekly quiz target verified')
                  ON CONFLICT(student_id,task_id) DO NOTHING'''),{'sid':sid,'task':task['id'],'xp':task['xp_reward']})
    db.commit();updated=_load_quiz(db,q,sid)
    return {'correct':correct,'xp_awarded':gained,'feedback':'Correct reasoning checkpoint. Explain why that step follows.' if correct else 'Review the applicable principle and try again; no XP deducted.', 'quiz':updated}

@router.get('/student/progress')
def senior_progress(db:Session=Depends(get_db),user:User=Depends(roles_allowed('student'))):
    sid=senior_sid(db,user)
    from backend.app.agent.progress import student_weekly_progress
    result=student_weekly_progress(db,sid)
    return {**result,'weekly_teacher_plans':result['plans'],'step_xp':db.execute(text('SELECT COALESCE(SUM(points),0) FROM public.senior_step_xp WHERE student_id=:sid'),{'sid':sid}).scalar_one()}

@router.get('/teacher/quizzes/{quiz_id}/submissions')
def teacher_submissions(quiz_id:int,db:Session=Depends(get_db),user:User=Depends(roles_allowed('teacher'))):
    owned=db.execute(text('''SELECT 1 FROM public.senior_reasoning_quizzes q
      JOIN public.teachers t ON t.teacher_id=q.teacher_id AND t.school_id=q.school_id
      WHERE q.id=:qid AND t.user_id=:uid'''),{'qid':quiz_id,'uid':user.user_id}).scalar()
    if not owned:raise HTTPException(404,'Quiz unavailable')
    return [dict(r) for r in db.execute(text('''SELECT a.id,a.student_id,us.first_name,us.last_name,s.position AS step_position,
       a.response_text,a.reasoning_text,a.is_correct,a.submitted_at,a.teacher_feedback,a.reviewed_at
      FROM public.senior_reasoning_attempts a
      JOIN public.senior_reasoning_steps s ON s.id=a.step_id
      JOIN public.senior_reasoning_quizzes q ON q.id=s.quiz_id
      JOIN public.students st ON st.student_id=a.student_id
      JOIN public.users us ON us.user_id=st.user_id
      WHERE q.id=:qid ORDER BY a.submitted_at DESC LIMIT 200'''),{'qid':quiz_id}).mappings()]

class TeacherReview(BaseModel):
    feedback:str=Field(min_length=4,max_length=1500)

@router.post('/teacher/attempts/{attempt_id}/review')
def teacher_review(attempt_id:int,payload:TeacherReview,db:Session=Depends(get_db),user:User=Depends(roles_allowed('teacher'))):
    row=db.execute(text('''UPDATE public.senior_reasoning_attempts a
      SET teacher_feedback=:feedback,reviewed_at=now(),reviewed_by_user_id=:uid
      FROM public.senior_reasoning_steps s,public.senior_reasoning_quizzes q,public.teachers t
      WHERE a.id=:id AND a.step_id=s.id AND s.quiz_id=q.id
      AND q.teacher_id=t.teacher_id AND q.school_id=t.school_id AND t.user_id=:uid RETURNING a.id'''),
      {'id':attempt_id,'feedback':payload.feedback,'uid':user.user_id}).scalar_one_or_none()
    if not row:raise HTTPException(404,'Submission unavailable')
    db.commit();return {'reviewed':True,'attempt_id':row}

class DraftGeneration(BaseModel):
    document_id:int
    lesson_key:str=Field(min_length=3,max_length=60)
    count:int=Field(default=2,ge=1,le=3)

@router.post('/teacher/generate',status_code=201)
async def generate_drafts(payload:DraftGeneration,db:Session=Depends(get_db),user:User=Depends(roles_allowed('teacher'))):
    """Draft generation uses OpenRouter; teacher must review answers before approval.

    The lesson ID must match a chunk in the teacher's own published document.
    """
    import os, httpx
    from dotenv import load_dotenv
    from backend.app.core.config import PROJECT_ROOT
    load_dotenv(PROJECT_ROOT/'.env')
    if not owner(db,payload.document_id,user.user_id):raise HTTPException(403,'Document not assigned to you')
    chunks=db.execute(text('SELECT id,content FROM public.teacher_curriculum_chunks WHERE document_id=:id ORDER BY chunk_index'),{'id':payload.document_id}).mappings().all()
    source=next((c for c in chunks if payload.lesson_key.lower() in c['content'].lower()),None)
    if not source:raise HTTPException(422,'The lesson key was not found in your uploaded document. Use a code like G11-M01.')
    key=os.getenv('OPENROUTER_API_KEY','').strip()
    if not key:raise HTTPException(503,'Set OPENROUTER_API_KEY to generate drafts, or import the provided JSON bank instead')
    instructions=(
      'You are preparing teacher-review-only advanced mathematics quizzes. '
      'Return a JSON object with key questions: a list of EXACTLY '+str(payload.count)+' objects. '
      'Each object requires lesson_key, title, statement, source_terms (list of topic words), '
      'teacher_explanation, and steps (3 items). Each step requires prompt, expected_answer, '
      'check_type numeric or exact, hint, xp=8. All steps must be objectively gradeable '
      'with deterministic numeric/exact matching, not subjective proofs. Each prompt must require '
      'a justified intermediate result. Never assert that generated solutions are teacher-approved. '
      'Follow ONLY the provided course excerpt. Return JSON only.'
    )
    try:
        async with httpx.AsyncClient(timeout=45) as client:
            response=await client.post('https://openrouter.ai/api/v1/chat/completions',headers={'Authorization':f'Bearer {key}'},json={
                'model':os.getenv('OPENROUTER_MODEL','openai/gpt-4o-mini'),
                'temperature':0.1,'max_tokens':1800,'messages':[{'role':'system','content':instructions},
                    {'role':'user','content':f"Lesson {payload.lesson_key}\nSource excerpt:\n{source['content'][:6500]}"}]})
            response.raise_for_status()
        raw=response.json()['choices'][0]['message']['content'].strip()
        if raw.startswith('```'):
            raw=raw.split('\n',1)[-1].rsplit('```',1)[0].strip()
        parsed=json.loads(raw)
        questions=parsed['questions']
        if not isinstance(questions,list) or len(questions)!=payload.count:raise ValueError('Unexpected question count')
        for q in questions:
            q['lesson_key']=payload.lesson_key
            q['source_terms']=[payload.lesson_key]
            if len(q.get('steps',[]))!=3:raise ValueError('Three steps required')
        # Trust boundaries and ownership rechecked in shared importer.
        return teacher_import(PackImport(document_id=payload.document_id,questions=questions),db,user)
    except (ValueError,KeyError,IndexError,json.JSONDecodeError) as exc:
        raise HTTPException(502,f'Generated draft structure requires correction: {type(exc).__name__}') from exc
    except httpx.HTTPError as exc:
        raise HTTPException(503,'OpenRouter is unavailable; please import your JSON quiz bank') from exc
