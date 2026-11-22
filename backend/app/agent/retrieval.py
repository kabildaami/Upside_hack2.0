"""Server-side class/subject-scoped RAG. Never retrieve teacher answer keys."""
from sqlalchemy import text
from backend.app.services.rag_student import rank_chunks

SCOPE='''
 FROM public.students st
 JOIN public.student_enrollments e ON e.student_id=st.student_id AND e.school_id=st.school_id AND e.ended_at IS NULL
 JOIN public.teacher_curriculum_documents d ON d.class_id=e.class_id AND d.school_id=e.school_id AND d.status='ready'
 JOIN public.teacher_classes tc ON tc.teacher_id=d.teacher_id AND tc.class_id=d.class_id AND tc.school_id=d.school_id AND tc.subject_id=d.subject_id
 JOIN public.teacher_curriculum_chunks ch ON ch.document_id=d.id
 WHERE st.student_id=:sid
'''

def authorized_retrieve(db, student_id:int, question:str, document_id:int|None=None, limit:int=4)->list[dict]:
    doc_filter=' AND d.id=:docid' if document_id is not None else ''
    query=text('''SELECT ch.id AS chunk_id,ch.document_id,ch.chunk_index,ch.page_number,ch.heading,ch.content,d.title
    '''+SCOPE+doc_filter+''' ORDER BY d.id DESC,ch.chunk_index LIMIT 2000''')
    rows=[dict(r) for r in db.execute(query, {'sid':student_id,**({'docid':document_id} if document_id is not None else {})}).mappings()]
    safe=[]
    for row in rows:
        # Teacher-only answer sections must never appear in tutor context.
        txt=row['content']
        for sentinel in ('TEACHER ANSWER KEY','ANSWER KEY — TEACHER ONLY','Corrigé réservé à l’enseignant','SECTION NON DESTINÉE'):
            if sentinel.casefold() in txt.casefold():
                txt=txt[:txt.casefold().index(sentinel.casefold())]
        if txt.strip():safe.append({**row,'content':txt[:3500]})
    return rank_chunks(question,safe,limit=limit)
