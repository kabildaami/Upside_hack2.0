"""SQL-backed deterministic weekly plan tracking. Never LLM-derived percentages."""
from sqlalchemy import text

def student_weekly_progress(db,sid:int):
    plans=db.execute(text('''
      SELECT DISTINCT p.id,p.title,p.week_start,p.week_end,p.class_id,p.subject_id,s.subject_name
      FROM public.edunova_weekly_plans p
      JOIN public.subjects s ON s.subject_id=p.subject_id
      JOIN public.student_enrollments e ON e.class_id=p.class_id AND e.school_id=p.school_id AND e.ended_at IS NULL
      WHERE e.student_id=:sid AND p.published=true AND p.week_end>=CURRENT_DATE-7
      ORDER BY p.week_start DESC,p.id DESC LIMIT 6
    '''),{'sid':sid}).mappings().all()
    output=[]
    for plan in plans:
        tasks=[dict(t) for t in db.execute(text('''SELECT t.id,t.title,t.kind,t.lesson_key,t.target_correct,t.xp_reward,
        sp.completed_at,COALESCE(sp.correct_count,0) AS correct_count
        FROM public.edunova_plan_tasks t LEFT JOIN public.edunova_student_task_progress sp
        ON sp.task_id=t.id AND sp.student_id=:sid WHERE t.plan_id=:pid ORDER BY t.position,t.id'''),{'sid':sid,'pid':plan['id']}).mappings()]
        total=len(tasks);done=sum(1 for t in tasks if t['completed_at'])
        output.append({**dict(plan),'tasks':[{**t,'completed':bool(t['completed_at'])} for t in tasks],
                       'percent':round(100*done/total) if total else 0,'completed_count':done,'total_count':total})
    xp=db.execute(text('SELECT COALESCE(SUM(points),0) FROM public.edunova_xp_events WHERE student_id=:sid'),{'sid':sid}).scalar_one()
    # The extra ledger exists only after migration 12; support existing junior databases safely.
    if db.execute(text("SELECT to_regclass('public.senior_step_xp')")).scalar():
        xp+=db.execute(text('SELECT COALESCE(SUM(points),0) FROM public.senior_step_xp WHERE student_id=:sid'),{'sid':sid}).scalar_one()
    return {'plans':output,'xp':xp,'total_tasks':sum(p['total_count'] for p in output),'done_tasks':sum(p['completed_count'] for p in output)}
