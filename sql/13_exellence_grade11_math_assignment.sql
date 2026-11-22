-- TEST FIXTURE ONLY: add mathematics assignment to existing 11A teacher Yassine.
-- Keeps his Physics assignment; does not alter grades or student enrollment.
BEGIN;
INSERT INTO public.teacher_classes(teacher_id,class_id,school_id,subject_id)
SELECT t.teacher_id,c.class_id,c.school_id,sub.subject_id
FROM public.teachers t
JOIN public.users u ON u.user_id=t.user_id
JOIN public.classes c ON c.school_id=t.school_id
JOIN public.schools sc ON sc.school_id=c.school_id
JOIN public.users du ON du.user_id=sc.director_user_id
JOIN public.subjects sub ON sub.subject_name='Mathematics' AND sub.school_level='high_school'
WHERE u.email='yassine@exellence.com'
AND du.email='nadia@exellence.com'
AND c.class_name='11A' AND c.grade_level='11th grade' AND c.academic_year='2026-2027'
ON CONFLICT(teacher_id,class_id,subject_id) DO NOTHING;
COMMIT;
