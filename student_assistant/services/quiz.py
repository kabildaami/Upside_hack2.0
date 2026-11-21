import json
from .db import query,require_student
from .student import recent_progress

def create_quiz(student_id,subject,concept,source_chunk_id,question,options,answer_index,hint='',difficulty=1):
    require_student(student_id)
    if not 2<=len(options)<=5 or not 0<=answer_index<len(options):raise ValueError('Invalid options')
    if difficulty not in range(1,6):raise ValueError('Invalid difficulty')
    return query('''INSERT INTO assistant.quiz_items(student_id,subject,concept_key,source_chunk_id,question,options,answer_index,hint,difficulty,status)
     VALUES(%s,%s,%s,%s,%s,%s::jsonb,%s,%s,%s,'draft') RETURNING id''',
     (student_id,subject,concept,source_chunk_id,question,json.dumps(options),answer_index,hint,difficulty),fetch='one')

def take_quiz(student_id,quiz_id):
    require_student(student_id)
    # Answer key deliberately not exposed to student-facing tools.
    return query('''SELECT id,subject,concept_key,question,options,hint,difficulty FROM assistant.quiz_items
      WHERE student_id=%s AND id=%s AND status IN ('draft','validated','reviewed')''',(student_id,quiz_id),fetch='one')

def grade(student_id,quiz_id,chosen_index,hints_used=0,response_seconds=None):
    require_student(student_id)
    with __import__('contextlib').nullcontext():
      from .db import connection
      with connection() as conn,conn.cursor() as cur:
        cur.execute('SELECT subject,concept_key,answer_index FROM assistant.quiz_items WHERE id=%s AND student_id=%s FOR UPDATE',(quiz_id,student_id))
        item=cur.fetchone()
        if not item: raise ValueError('Question not found')
        correct=(chosen_index==item['answer_index'])
        cur.execute('''INSERT INTO assistant.quiz_attempts(student_id,quiz_item_id,selected_index,is_correct,hints_used,response_seconds)
          VALUES(%s,%s,%s,%s,%s,%s) ON CONFLICT(student_id,quiz_item_id) DO NOTHING RETURNING id''',
          (student_id,quiz_id,chosen_index,correct,hints_used,response_seconds))
        inserted=cur.fetchone()
        if not inserted: return {'status':'already_answered','is_correct':correct}
        cur.execute('''INSERT INTO assistant.concept_mastery(student_id,subject,concept_key,attempts,correct,independent_correct,hints_used,mastery_score,last_practiced_at,next_review_on)
          VALUES(%s,%s,%s,1,%s,%s,%s,%s,now(),CURRENT_DATE+3)
          ON CONFLICT(student_id,subject,concept_key) DO UPDATE SET
           attempts=concept_mastery.attempts+1,correct=concept_mastery.correct+EXCLUDED.correct,
           independent_correct=concept_mastery.independent_correct+EXCLUDED.independent_correct,
           hints_used=concept_mastery.hints_used+EXCLUDED.hints_used,
           mastery_score=LEAST(1,GREATEST(0,(concept_mastery.mastery_score*0.75+EXCLUDED.mastery_score*0.25))),
           last_practiced_at=now(),next_review_on=CURRENT_DATE+3''',
          (student_id,item['subject'],item['concept_key'],int(correct),int(correct and hints_used==0),hints_used,0.8 if correct and hints_used==0 else 0.65 if correct else 0.25))
        return {'status':'graded','is_correct':correct,'hint':'Try a similar example if incorrect.'}
