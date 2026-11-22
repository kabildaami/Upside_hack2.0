"""Server-authoritative grade routing, student preferences, and study-session API."""
import re
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.tables import User
from backend.app.security.dependencies import roles_allowed

router = APIRouter(prefix='/student/experience', tags=['student experience'])

from backend.app.api.grade_utils import parse_grade

def student_context(db: Session, user: User):
    row = db.execute(text('''
      SELECT st.student_id,c.grade_level AS class_grade,sv.grade_level AS survey_grade,
             c.class_name,sc.school_name
      FROM public.students st
      JOIN public.schools sc ON sc.school_id=st.school_id
      LEFT JOIN public.student_enrollments e ON e.student_id=st.student_id AND e.school_id=st.school_id AND e.ended_at IS NULL
      LEFT JOIN public.classes c ON c.class_id=e.class_id AND c.school_id=st.school_id
      LEFT JOIN public.student_survey sv ON sv.student_id=st.student_id
      WHERE st.user_id=:uid ORDER BY e.enrolled_at DESC NULLS LAST LIMIT 1
    '''), {'uid':user.user_id}).mappings().first()
    if not row: raise HTTPException(404, 'Student record not found')
    class_grade = parse_grade(row['class_grade'])
    survey_grade = parse_grade(row['survey_grade'])
    # Class enrollment is authoritative; inconsistencies are surfaced rather than silently overwritten.
    grade = class_grade or survey_grade
    if grade is None: raise HTTPException(409, 'Student grade is missing or invalid; contact school admin')
    if class_grade is not None and survey_grade is not None and class_grade != survey_grade:
        raise HTTPException(409, 'Student class grade and survey grade disagree; contact school admin')
    return row, grade

DEFAULTS = dict(avatar_key='fox',preferred_style='quest',read_aloud=False,easy_words=False,short_sessions=True,calm_mode=False,large_text=False)

class Preferences(BaseModel):
    model_config = ConfigDict(extra='forbid')
    avatar_key: Literal['fox','rabbit','penguin','turtle','cat','owl'] = 'fox'
    preferred_style: Literal['quest','story','draw','guided','focus','review'] = 'quest'
    read_aloud: bool = False
    easy_words: bool = False
    short_sessions: bool = True
    calm_mode: bool = False
    large_text: bool = False

class SessionStart(BaseModel):
    subject_name: str
    activity_type: Literal['quest','guided','focus','review']

@router.get('/me')
def experience_me(user: User=Depends(roles_allowed('student')),db: Session=Depends(get_db)):
    row,grade=student_context(db,user)
    prefs=db.execute(text('SELECT avatar_key,preferred_style,read_aloud,easy_words,short_sessions,calm_mode,large_text FROM public.student_ui_preferences WHERE student_id=:sid'),{'sid':row['student_id']}).mappings().first()
    return {'student_id':row['student_id'],'grade':grade,'variant':'junior' if grade<=6 else 'senior',
            'grade_label':row['class_grade'] or row['survey_grade'],'class_name':row['class_name'],
            'school_name':row['school_name'],'preferences':dict(prefs) if prefs else DEFAULTS}

@router.put('/preferences')
def save_preferences(payload: Preferences,user: User=Depends(roles_allowed('student')),db: Session=Depends(get_db)):
    row,grade=student_context(db,user)
    fields=payload.model_dump()
    if grade <= 6 and fields['preferred_style'] not in ('quest','story','draw'):
        raise HTTPException(422,'Unsupported learning style for primary students')
    if grade >= 7 and fields['preferred_style'] not in ('guided','focus','review'):
        raise HTTPException(422,'Unsupported learning style for senior students')
    db.execute(text('''INSERT INTO public.student_ui_preferences
     (student_id,avatar_key,preferred_style,read_aloud,easy_words,short_sessions,calm_mode,large_text)
     VALUES (:student_id,:avatar_key,:preferred_style,:read_aloud,:easy_words,:short_sessions,:calm_mode,:large_text)
     ON CONFLICT(student_id) DO UPDATE SET
     avatar_key=EXCLUDED.avatar_key,preferred_style=EXCLUDED.preferred_style,
     read_aloud=EXCLUDED.read_aloud,easy_words=EXCLUDED.easy_words,
     short_sessions=EXCLUDED.short_sessions,calm_mode=EXCLUDED.calm_mode,
     large_text=EXCLUDED.large_text,updated_at=now()'''), {'student_id':row['student_id'],**fields})
    db.commit()
    return {'ok':True,'preferences':fields}

@router.post('/sessions')
def start_session(payload:SessionStart,user:User=Depends(roles_allowed('student')),db:Session=Depends(get_db)):
    row,grade=student_context(db,user)
    subject=payload.subject_name.strip()
    if not (2<=len(subject)<=100): raise HTTPException(422,'Invalid subject name')
    if grade<=6 and payload.activity_type not in ('quest','guided'):
        raise HTTPException(422,'Invalid session mode for grade')
    if grade>=7 and payload.activity_type not in ('guided','focus','review'):
        raise HTTPException(422,'Invalid session mode for grade')
    # Resume an existing unfinished study session rather than duplicating it.
    active=db.execute(text('SELECT id,subject_name,activity_type,started_at FROM public.student_learning_sessions WHERE student_id=:sid AND ended_at IS NULL ORDER BY id DESC LIMIT 1'),{'sid':row['student_id']}).mappings().first()
    if active: return {'session':dict(active),'resumed':True}
    session=db.execute(text('INSERT INTO public.student_learning_sessions(student_id,subject_name,activity_type) VALUES (:sid,:subject,:kind) RETURNING id,subject_name,activity_type,started_at'),{'sid':row['student_id'],'subject':subject,'kind':payload.activity_type}).mappings().first()
    db.commit()
    return {'session':dict(session),'resumed':False}

@router.post('/sessions/{session_id}/finish')
def finish_session(session_id:int,user:User=Depends(roles_allowed('student')),db:Session=Depends(get_db)):
    row,_=student_context(db,user)
    result=db.execute(text('''UPDATE public.student_learning_sessions SET ended_at=now()
      WHERE id=:id AND student_id=:sid AND ended_at IS NULL RETURNING id,ended_at'''),{'id':session_id,'sid':row['student_id']}).mappings().first()
    if not result: raise HTTPException(404,'Active session not found')
    db.commit()
    return dict(result)

@router.get('/sessions')
def list_sessions(user:User=Depends(roles_allowed('student')),db:Session=Depends(get_db)):
    row,_=student_context(db,user)
    rows=db.execute(text('SELECT id,subject_name,activity_type,started_at,ended_at FROM public.student_learning_sessions WHERE student_id=:sid ORDER BY started_at DESC LIMIT 30'),{'sid':row['student_id']}).mappings().all()
    return [dict(r) for r in rows]
