# RAG demo API: only the logged-in student's authorized teacher curriculum.
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.tables import User
from backend.app.security.dependencies import roles_allowed
from backend.app.services.rag_student import generate_answer, rank_chunks

router = APIRouter(prefix='/student/rag',tags=['Student curriculum assistant'])

DOC_SCOPE = '''
  FROM public.students st
  JOIN public.student_enrollments e ON e.student_id=st.student_id
      AND e.school_id=st.school_id AND e.ended_at IS NULL
  JOIN public.teacher_curriculum_documents d ON d.class_id=e.class_id
      AND d.school_id=e.school_id AND d.status='ready'
  JOIN public.teacher_classes tc ON tc.teacher_id=d.teacher_id
      AND tc.school_id=d.school_id AND tc.class_id=d.class_id AND tc.subject_id=d.subject_id
  JOIN public.classes c ON c.class_id=e.class_id AND c.school_id=e.school_id
  JOIN public.subjects s ON s.subject_id=d.subject_id
  JOIN public.teachers t ON t.teacher_id=d.teacher_id AND t.school_id=d.school_id
  JOIN public.users tu ON tu.user_id=t.user_id
'''

class StudentQuestion(BaseModel):
    question: str = Field(min_length=3,max_length=800)
    document_id: int | None = Field(default=None,ge=1)

@router.get('/documents')
def my_documents(user:User=Depends(roles_allowed('student')),db:Session=Depends(get_db)):
    records=db.execute(text('''
      SELECT DISTINCT d.id,d.title,d.chunk_count,d.original_filename,c.class_name,
         s.subject_name,tu.first_name AS teacher_first_name,tu.last_name AS teacher_last_name
      '''+DOC_SCOPE+''' WHERE st.user_id=:uid ORDER BY d.id DESC
    '''),{'uid':user.user_id}).mappings().all()
    return [dict(row) for row in records]

@router.post('/ask')
def ask(question:StudentQuestion,user:User=Depends(roles_allowed('student')),db:Session=Depends(get_db)):
    parameters={'uid':user.user_id,'docid':question.document_id}
    # SQL permission filtering occurs BEFORE retrieval and LLM context creation.
    # Capped to keep this prototype predictable on small uploaded curricula.
    chunks=db.execute(text('''
      SELECT ch.id AS chunk_id,ch.document_id,ch.chunk_index,ch.page_number,ch.heading,ch.content,
             d.title,s.subject_name,c.class_name,
             tu.first_name AS teacher_first_name,tu.last_name AS teacher_last_name
      '''+DOC_SCOPE+'''
      JOIN public.teacher_curriculum_chunks ch ON ch.document_id=d.id
      AND (CAST(:docid AS INTEGER) IS NULL OR d.id=CAST(:docid AS INTEGER))
      WHERE st.user_id=:uid ORDER BY d.id DESC,ch.chunk_index ASC LIMIT 2000
    '''),parameters).mappings().all()
    if question.document_id is not None and not chunks:
        # Avoid existence disclosures: unknown or unauthorized documents are indistinguishable.
        raise HTTPException(404,'This document is not available in your class.')
    if not chunks:
        return {'question':question.question,'answer':'There is no processed curriculum uploaded for your class yet. Ask your teacher to upload a document.',
                'mode':'no-documents','sources':[]}
    matched=rank_chunks(question.question,[dict(row) for row in chunks],limit=5)
    if not matched:
        return {'question':question.question,'answer':'I could not find this topic in the lesson documents available to your class. Try different words or ask your teacher.',
                'mode':'no-match','sources':[]}
    answer,mode=generate_answer(question.question,matched)
    citations=[{k:row[k] for k in ('chunk_id','document_id','title','chunk_index','page_number','heading','subject_name','class_name','teacher_first_name','teacher_last_name','score')} | {'excerpt':row['content'][:800]} for row in matched]
    return {'question':question.question,'answer':answer,'mode':mode,'sources':citations}
