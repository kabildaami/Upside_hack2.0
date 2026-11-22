from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.tables import User, Student, StudentSurvey, Hobby, SpecialNeed, StudyProblem, Subject
from backend.app.schemas.api import LabelOut, SubjectOut, StudentOut, SurveyOut
from backend.app.security.dependencies import current_user, roles_allowed

router = APIRouter()

@router.get('/health/db', tags=['health'])
def db_health(db: Session = Depends(get_db)):
    return {'status': 'ok', 'postgresql': db.execute(text('SELECT current_database()')).scalar_one()}

@router.get('/catalog', tags=['catalog'])
def catalog(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return {
        'hobbies': [LabelOut.model_validate(x) for x in db.scalars(select(Hobby).order_by(Hobby.id))],
        'special_needs': [LabelOut.model_validate(x) for x in db.scalars(select(SpecialNeed).order_by(SpecialNeed.id))],
        'study_problems': [LabelOut.model_validate(x) for x in db.scalars(select(StudyProblem).order_by(StudyProblem.id))],
        'subjects': [SubjectOut.model_validate(x) for x in db.scalars(select(Subject).order_by(Subject.subject_id))]
    }

def can_access_student(db: Session, user: User, student: Student) -> bool:
    if user.role == 'admin':
        return True
    if user.role == 'student':
        return student.user_id == user.user_id
    if user.role == 'parent':
        return db.execute(text('SELECT 1 FROM public.guardian_student_links l JOIN public.parents p ON p.parent_id=l.parent_id WHERE p.user_id=:uid AND l.student_id=:sid AND l.can_view_progress=true'), {'uid': user.user_id, 'sid': student.student_id}).first() is not None
    if user.role == 'teacher':
        return db.execute(text('SELECT 1 FROM public.teachers t JOIN public.teacher_classes tc ON tc.teacher_id=t.teacher_id JOIN public.student_enrollments e ON e.class_id=tc.class_id AND e.school_id=tc.school_id WHERE t.user_id=:uid AND e.student_id=:sid AND e.ended_at IS NULL'), {'uid': user.user_id, 'sid': student.student_id}).first() is not None
    if user.role == 'director':
        return db.execute(text('SELECT 1 FROM public.schools WHERE director_user_id=:uid AND school_id=:school'), {'uid': user.user_id, 'school': student.school_id}).first() is not None
    return False

@router.get('/students/{student_id}', response_model=StudentOut, tags=['students'])
def get_student(student_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(404, 'Student not found')
    if not can_access_student(db, user, student):
        raise HTTPException(403, 'Student not accessible')
    return student

@router.get('/students/{student_id}/survey', response_model=SurveyOut, tags=['surveys'])
def get_survey(student_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(404, 'Student not found')
    # Sensitive form information: student and admin only for this demo.
    if user.role != 'admin' and not (user.role == 'student' and user.user_id == student.user_id):
        raise HTTPException(403, 'Survey not accessible')
    survey = db.get(StudentSurvey, student_id)
    if survey is None:
        raise HTTPException(404, 'Survey not found')
    return survey

@router.get('/dashboards/student', tags=['dashboards'])
def student_dashboard(user: User = Depends(roles_allowed('student')), db: Session = Depends(get_db)):
    student = db.scalar(select(Student).where(Student.user_id==user.user_id))
    return {'space': 'student', 'student_id': student.student_id if student else None, 'message': 'Learning workspace'}

@router.get('/dashboards/parent', tags=['dashboards'])
def parent_dashboard(user: User = Depends(roles_allowed('parent')), db: Session = Depends(get_db)):
    rows = db.execute(text('SELECT l.student_id FROM public.guardian_student_links l JOIN public.parents p ON p.parent_id=l.parent_id WHERE p.user_id=:uid AND l.can_view_progress=true'), {'uid': user.user_id}).all()
    return {'space': 'parent', 'student_ids': [r.student_id for r in rows]}

@router.get('/dashboards/teacher', tags=['dashboards'])
def teacher_dashboard(user: User = Depends(roles_allowed('teacher')), db: Session = Depends(get_db)):
    rows = db.execute(text('SELECT DISTINCT tc.class_id FROM public.teacher_classes tc JOIN public.teachers t ON t.teacher_id=tc.teacher_id WHERE t.user_id=:uid'), {'uid': user.user_id}).all()
    return {'space': 'teacher', 'class_ids': [r.class_id for r in rows]}

@router.get('/dashboards/director', tags=['dashboards'])
def director_dashboard(user: User = Depends(roles_allowed('director')), db: Session = Depends(get_db)):
    rows = db.execute(text('SELECT school_id FROM public.schools WHERE director_user_id=:uid'), {'uid': user.user_id}).all()
    return {'space': 'director', 'school_ids': [r.school_id for r in rows]}

@router.get('/dashboards/admin', tags=['dashboards'])
def admin_dashboard(user: User = Depends(roles_allowed('admin')), db: Session = Depends(get_db)):
    return {'space': 'admin', 'total_users': db.scalar(select(__import__('sqlalchemy').func.count()).select_from(User))}
