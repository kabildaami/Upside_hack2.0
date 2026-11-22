"""School enrollment requests. No account is created until school staff act separately."""
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, ConfigDict, field_validator
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.tables import User
from backend.app.security.dependencies import current_user

router = APIRouter(prefix='/admissions', tags=['admissions'])

class Application(BaseModel):
    model_config = ConfigDict(extra='forbid')
    school_id: int = Field(gt=0)
    full_name: str = Field(min_length=2, max_length=120)
    age: int = Field(ge=5, le=99)
    contact: str = Field(min_length=5, max_length=120)
    field_of_study: str = Field(default='', max_length=120)
    level: str = Field(default='', max_length=40)
    other_hobbies: str = Field(default='', max_length=500)
    needs_details: str = Field(default='', max_length=1000)
    difficult_subjects: str = Field(default='', max_length=500)
    difficulty_level: int = Field(default=3, ge=1, le=5)
    help_wanted: str = Field(default='', max_length=1000)
    hobbies: list[int] = Field(default_factory=list, max_length=40)
    special_needs: list[int] = Field(default_factory=list, max_length=40)
    study_problems: list[int] = Field(default_factory=list, max_length=40)
    difficult_subject_ids: list[int] = Field(default_factory=list, max_length=40)
    consent: Literal[True]
    guardian_consent_confirmed: bool = False

    @field_validator('full_name', 'contact')
    @classmethod
    def strip_required(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('Cannot be empty')
        return v

    @field_validator('hobbies', 'special_needs', 'study_problems', 'difficult_subject_ids')
    @classmethod
    def unique_positive_ids(cls, v: list[int]) -> list[int]:
        if any(isinstance(x, bool) or x <= 0 for x in v) or len(v) != len(set(v)):
            raise ValueError('Options must be unique positive IDs')
        return v

class StatusChange(BaseModel):
    status: Literal['contacted', 'declined']

@router.get('/options')
def options(db: Session = Depends(get_db)):
    def query(sql):
        return [dict(r) for r in db.execute(text(sql)).mappings()]
    return {
        'schools': query('SELECT school_id AS id, school_name AS label FROM public.schools ORDER BY school_name'),
        'hobbies': query('SELECT id,label FROM public.hobbies ORDER BY label'),
        'special_needs': query('SELECT id,label FROM public.special_needs ORDER BY label'),
        'study_problems': query('SELECT id,label FROM public.study_problems ORDER BY label'),
        'subjects': query('SELECT subject_id AS id, subject_name AS label, school_level FROM public.subjects ORDER BY school_level,subject_name'),
    }

@router.post('/apply', status_code=status.HTTP_201_CREATED)
def apply(payload: Application, db: Session = Depends(get_db)):
    if payload.age < 18 and not payload.guardian_consent_confirmed:
        raise HTTPException(422, 'Parent or guardian confirmation is required for applicants under 18')
    if not db.scalar(text('SELECT EXISTS(SELECT 1 FROM public.schools WHERE school_id=:id)'), {'id': payload.school_id}):
        raise HTTPException(422, 'Invalid school')
    for field, table, column in (
        ('hobbies', 'hobbies', 'id'), ('special_needs', 'special_needs', 'id'),
        ('study_problems', 'study_problems', 'id'), ('difficult_subject_ids', 'subjects', 'subject_id'),
    ):
        vals = getattr(payload, field)
        if vals:
            found = db.scalar(text(f'SELECT COUNT(*) FROM public.{table} WHERE {column} = ANY(:ids)'), {'ids': vals})
            if found != len(vals):
                raise HTTPException(422, f'Invalid selection in {field}')
    data = payload.model_dump()
    data['full_name'] = data['full_name'].strip()
    data['contact'] = data['contact'].strip()
    result = db.execute(text('''
        INSERT INTO public.student_admission_requests (
          school_id,full_name,age,contact,field_of_study,level,other_hobbies,needs_details,
          difficult_subjects,difficulty_level,help_wanted,hobbies,special_needs,study_problems,
          difficult_subject_ids,consent,guardian_consent_confirmed
        ) VALUES (
          :school_id,:full_name,:age,:contact,:field_of_study,:level,:other_hobbies,:needs_details,
          :difficult_subjects,:difficulty_level,:help_wanted,:hobbies,:special_needs,:study_problems,
          :difficult_subject_ids,:consent,:guardian_consent_confirmed
        ) RETURNING id
    '''), data)
    application_id = result.scalar_one()
    db.commit()
    return {'request_id': application_id, 'status':'pending',
            'message':'Your request has been sent. The school director will contact you directly.'}

@router.get('/requests')
def list_requests(user: User = Depends(current_user), db: Session = Depends(get_db)):
    if user.role not in ('director', 'admin'):
        raise HTTPException(403, 'Director access required')
    # A director sees only applications for the school they direct.
    where = 'WHERE s.director_user_id=:uid' if user.role == 'director' else ''
    result = db.execute(text(f'''SELECT a.* , s.school_name FROM public.student_admission_requests a
      JOIN public.schools s ON s.school_id = a.school_id {where}
      ORDER BY a.created_at DESC LIMIT 200'''), {'uid':user.user_id})
    return [dict(r) for r in result.mappings()]

@router.patch('/requests/{request_id}')
def change_status(request_id: int, payload: StatusChange, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if user.role not in ('director', 'admin'):
        raise HTTPException(403, 'Director access required')
    where = 'AND s.director_user_id=:uid' if user.role == 'director' else ''
    id_row = db.execute(text(f'''SELECT a.id FROM public.student_admission_requests a
       JOIN public.schools s ON s.school_id=a.school_id WHERE a.id=:rid {where}'''),
       {'uid':user.user_id, 'rid':request_id}).first()
    if id_row is None:
        raise HTTPException(404, 'Request not found')
    db.execute(text('''UPDATE public.student_admission_requests
        SET status=:status, handled_by=:uid, updated_at=now() WHERE id=:rid'''),
        {'status':payload.status, 'uid':user.user_id, 'rid':request_id})
    db.commit()
    return {'id':request_id,'status':payload.status}
