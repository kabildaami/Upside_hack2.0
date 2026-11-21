from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from .config import STUDENT_TIMEZONE
from .db import query,require_student

def clock(tz=STUDENT_TIMEZONE):
    if tz not in ('Africa/Tunis','UTC','Europe/Paris','America/New_York'):
        tz=STUDENT_TIMEZONE
    now=datetime.now(ZoneInfo(tz))
    monday=(now+timedelta(days=(7-now.weekday()))).date()
    return {'today':now.date().isoformat(),'weekday':now.strftime('%A'),'local_time':now.isoformat(),
            'timezone':tz,'next_week_monday':monday.isoformat(),'next_week_sunday':(monday+timedelta(days=6)).isoformat()}

def goals(student_id,limit=20):
    require_student(student_id)
    return query('SELECT id,subject,goal,target_date,status FROM assistant.study_goals WHERE student_id=%s ORDER BY target_date LIMIT %s',(student_id,max(1,min(limit,50))))

def add_goal(student_id,subject,goal,target_date):
    require_student(student_id)
    if len(goal)>250: raise ValueError('Goal too long')
    return query('INSERT INTO assistant.study_goals(student_id,subject,goal,target_date) VALUES(%s,%s,%s,%s) RETURNING id,target_date',(student_id,subject,goal,target_date),fetch='one')

def hobby_catalog(student_id):
    require_student(student_id)
    return query('''SELECT h.id,h.label,EXISTS(SELECT 1 FROM public.student_hobbies sh WHERE sh.student_id=%s AND sh.hobby_id=h.id) AS selected
      FROM public.hobbies h ORDER BY h.label''',(student_id,))
