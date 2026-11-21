from .db import query,require_student,connection
from .student import consented

def start_session(student_id,thread_id,subject='Mathematics'):
    require_student(student_id)
    return query('''INSERT INTO assistant.learning_sessions(student_id,thread_id,subject) VALUES(%s,%s,%s) RETURNING id''',(student_id,thread_id,subject),fetch='one')

def log_event(student_id,session_id,event_type,duration_seconds=0,payload=None):
    require_student(student_id)
    if not consented(student_id,'pacing_analytics'):return {'status':'skipped_no_consent'}
    allowed=('activity_started','activity_completed','hint_requested','answer_submitted','break_started','break_ended','student_feedback','idle_observed')
    if event_type not in allowed: raise ValueError('Invalid event type')
    if not 0<=duration_seconds<=7200: raise ValueError('Invalid duration')
    import json
    return query('''INSERT INTO assistant.activity_events(student_id,session_id,event_type,duration_seconds,payload)
      SELECT %s,s.id,%s,%s,%s::jsonb FROM assistant.learning_sessions s
      WHERE s.id=%s AND s.student_id=%s RETURNING id''',(student_id,event_type,duration_seconds,json.dumps(payload or {}),session_id,student_id),fetch='one')

def end_session(student_id,session_id):
    require_student(student_id)
    return query('''UPDATE assistant.learning_sessions s SET status='finished',ended_at=now(),
      active_seconds=COALESCE((SELECT SUM(duration_seconds) FROM assistant.activity_events WHERE session_id=s.id AND event_type='activity_completed'),0),
      break_seconds=COALESCE((SELECT SUM(duration_seconds) FROM assistant.activity_events WHERE session_id=s.id AND event_type='break_ended'),0),
      idle_seconds=COALESCE((SELECT SUM(duration_seconds) FROM assistant.activity_events WHERE session_id=s.id AND event_type='idle_observed'),0)
      WHERE s.id=%s AND s.student_id=%s RETURNING id,active_seconds,break_seconds''',(session_id,student_id),fetch='one')

def pacing(student_id):
    require_student(student_id)
    if not consented(student_id,'pacing_analytics'):
        return {'activity_minutes':12,'reason':'No pacing consent; default only','break_after_minutes':12}
    r=query('''SELECT ss.preferred_activity_minutes,
       AVG(CASE WHEN event_type='activity_completed' THEN duration_seconds END) AS avg_duration,
       COUNT(*) FILTER (WHERE event_type='activity_completed') AS n
       FROM assistant.student_settings ss LEFT JOIN assistant.activity_events e ON e.student_id=ss.student_id
       WHERE ss.student_id=%s GROUP BY ss.preferred_activity_minutes''',(student_id,),fetch='one')
    n=int((r or {}).get('n') or 0); preferred=int((r or {}).get('preferred_activity_minutes') or 12)
    # Conservative adaptation; cannot infer clinical attention span from click data.
    if n<3: minutes=preferred
    else: minutes=min(25,max(5,round(float(r['avg_duration'])/60)))
    return {'activity_minutes':minutes,'break_after_minutes':minutes,'observations':n,'reason':'Based on completed practice periods, not a clinical attention measure'}
