"""Read-only school-scoped portals for Exellence Academy login tests."""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.tables import User
from backend.app.security.dependencies import roles_allowed

router = APIRouter(prefix="/spaces", tags=["school portals"])

@router.get("/student")
def student_space(user: User = Depends(roles_allowed("student")), db: Session = Depends(get_db)):
    result = db.execute(text("""
        SELECT s.student_id, sc.school_name, c.class_name, sv.grade_level,
               sv.school_level, sv.difficulty_level,
               (SELECT count(*) FROM public.student_goals g WHERE g.student_id=s.student_id AND g.completed_at IS NULL) AS open_goals,
               (SELECT count(*) FROM public.student_mastery m WHERE m.student_id=s.student_id) AS tracked_concepts
        FROM public.students s
        JOIN public.schools sc ON sc.school_id=s.school_id
        LEFT JOIN public.student_enrollments e ON e.student_id=s.student_id AND e.ended_at IS NULL
        LEFT JOIN public.classes c ON c.class_id=e.class_id
        LEFT JOIN public.student_survey sv ON sv.student_id=s.student_id
        WHERE s.user_id=:uid ORDER BY c.class_name NULLS LAST LIMIT 1
    """), {"uid": user.user_id}).mappings().first()
    return {"space":"student", "account":user.email, "student":dict(result) if result else None}

@router.get("/parent")
def parent_space(user: User = Depends(roles_allowed("parent")), db: Session = Depends(get_db)):
    records = db.execute(text("""
        SELECT DISTINCT s.student_id, su.first_name, su.last_name, sc.school_name,
               c.class_name, c.grade_level
        FROM public.parents p
        JOIN public.guardian_student_links gl ON gl.parent_id=p.parent_id AND gl.can_view_progress=true
        JOIN public.students s ON s.student_id=gl.student_id
        JOIN public.users su ON su.user_id=s.user_id
        JOIN public.schools sc ON sc.school_id=s.school_id
        LEFT JOIN public.student_enrollments e ON e.student_id=s.student_id AND e.ended_at IS NULL
        LEFT JOIN public.classes c ON c.class_id=e.class_id
        WHERE p.user_id=:uid ORDER BY su.first_name, c.class_name
    """), {"uid":user.user_id}).mappings().all()
    # Deliberately excludes private surveys, chats, personal reflections and needs.
    return {"space":"parent", "account":user.email, "children":[dict(x) for x in records]}

@router.get("/teacher")
def teacher_space(user: User = Depends(roles_allowed("teacher")), db: Session = Depends(get_db)):
    classes = db.execute(text("""
        SELECT DISTINCT c.class_id,c.class_name,c.grade_level,sc.school_name,
          (SELECT count(DISTINCT e.student_id) FROM public.student_enrollments e
           WHERE e.class_id=c.class_id AND e.ended_at IS NULL) AS student_count
        FROM public.teachers t
        JOIN public.teacher_classes tc ON tc.teacher_id=t.teacher_id AND tc.school_id=t.school_id
        JOIN public.classes c ON c.class_id=tc.class_id AND c.school_id=tc.school_id
        JOIN public.schools sc ON sc.school_id=c.school_id
        WHERE t.user_id=:uid ORDER BY c.class_name
    """), {"uid":user.user_id}).mappings().all()
    roster = db.execute(text("""
        SELECT DISTINCT c.class_id, s.student_id, su.first_name, su.last_name,
                        c.class_name, c.grade_level
        FROM public.teachers t
        JOIN public.teacher_classes tc ON tc.teacher_id=t.teacher_id AND tc.school_id=t.school_id
        JOIN public.classes c ON c.class_id=tc.class_id AND c.school_id=tc.school_id
        JOIN public.student_enrollments e ON e.class_id=c.class_id AND e.school_id=c.school_id AND e.ended_at IS NULL
        JOIN public.students s ON s.student_id=e.student_id AND s.school_id=c.school_id
        JOIN public.users su ON su.user_id=s.user_id
        WHERE t.user_id=:uid ORDER BY c.class_name,su.first_name
    """), {"uid":user.user_id}).mappings().all()
    return {"space":"teacher", "account":user.email,
            "classes":[dict(c) for c in classes],"students":[dict(s) for s in roster]}

@router.get("/director")
def director_space(user: User = Depends(roles_allowed("director")), db: Session = Depends(get_db)):
    school = db.execute(text("""
       SELECT sc.school_id,sc.school_name,sc.city,
          (SELECT count(*) FROM public.teachers t WHERE t.school_id=sc.school_id) AS teacher_count,
          (SELECT count(*) FROM public.students s WHERE s.school_id=sc.school_id) AS student_count,
          (SELECT count(*) FROM public.classes c WHERE c.school_id=sc.school_id AND c.academic_year='2026-2027') AS class_count
       FROM public.schools sc WHERE sc.director_user_id=:uid
    """),{"uid":user.user_id}).mappings().first()
    return {"space":"director", "account":user.email,"school":dict(school) if school else None}
