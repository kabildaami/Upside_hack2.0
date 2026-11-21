from .db import query, require_student

def student_profile(student_id):
    require_student(student_id)
    return query('''SELECT s.student_id,u.first_name,s.date_of_birth,sv.grade_level,sv.school_level,
        sv.difficulty_level,sv.help_wanted,
        (SELECT array_agg(h.label) FROM public.student_hobbies x JOIN public.hobbies h ON h.id=x.hobby_id WHERE x.student_id=s.student_id) AS interests,
        (SELECT array_agg(j.subject_name) FROM public.student_difficult_subjects x JOIN public.subjects j ON j.subject_id=x.subject_id WHERE x.student_id=s.student_id) AS difficult_subjects,
        ss.age_variant,ss.locale,ss.timezone,ss.preferred_explanation,ss.preferred_activity_minutes,
        ss.pacing_opt_in,ss.memory_opt_in
        FROM public.students s JOIN public.users u ON u.user_id=s.user_id
        LEFT JOIN public.student_survey sv ON sv.student_id=s.student_id
        LEFT JOIN assistant.student_settings ss ON ss.student_id=s.student_id
        WHERE s.student_id=%s''',(student_id,),fetch='one')

def consented(student_id,purpose):
    r=query('SELECT granted FROM assistant.student_consents WHERE student_id=%s AND purpose=%s',(student_id,purpose),fetch='one')
    return bool(r and r['granted'])

def recent_progress(student_id,limit=10):
    require_student(student_id)
    return query('''SELECT subject,concept_key,attempts,correct,independent_correct,hints_used,mastery_score,last_practiced_at,next_review_on
        FROM assistant.concept_mastery WHERE student_id=%s ORDER BY last_practiced_at DESC NULLS LAST LIMIT %s''',
        (student_id,max(1,min(limit,30))))

def memory_search(student_id,term='',limit=5):
    require_student(student_id)
    if not consented(student_id,'learning_memory'):return []
    cap=max(1,min(limit,12))
    if term.strip():
        from .embeddings import embed
        vec='['+','.join(str(float(x)) for x in embed(term))+']'
        return query('''SELECT id,category,content,evidence_count,confidence,updated_at
          FROM assistant.learning_memories WHERE student_id=%s AND active AND
          (expires_at IS NULL OR expires_at>now()) AND embedding IS NOT NULL
          ORDER BY embedding <=> %s::vector ASC LIMIT %s''',(student_id,vec,cap))
    return query('''SELECT id,category,content,evidence_count,confidence,updated_at
      FROM assistant.learning_memories WHERE student_id=%s AND active AND (expires_at IS NULL OR expires_at>now())
      ORDER BY updated_at DESC LIMIT %s''',(student_id,cap))

def add_memory(student_id,category,content,source_session_id=None):
    require_student(student_id)
    if not consented(student_id,'learning_memory'):return {'status':'skipped_no_consent'}
    if category not in ('learning_preference','learning_progress','concept_gap','successful_strategy'):raise ValueError('Invalid category')
    if len(content)>800: raise ValueError('Memory too long')
    from .embeddings import embed
    vec='['+','.join(str(float(x)) for x in embed(content))+']'
    return query('''INSERT INTO assistant.learning_memories(student_id,category,content,source_session_id,embedding)
        VALUES(%s,%s,%s,%s,%s::vector) RETURNING id''',(student_id,category,content,source_session_id,vec),fetch='one')

def recent_thread(student_id,thread_id,limit=6):
    require_student(student_id)
    if not consented(student_id,'learning_memory'):return []
    return query('''SELECT role,message,created_at FROM assistant.conversation_turns
      WHERE student_id=%s AND thread_id=%s ORDER BY created_at DESC LIMIT %s''',
      (student_id,thread_id,max(1,min(limit,10))))[::-1]
