# Teacher curriculum upload and authorized retrieval
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import Response
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.tables import User
from backend.app.security.dependencies import roles_allowed
from backend.app.services.curriculum_processing import extract_pages, make_chunks

router = APIRouter(prefix='/curriculum', tags=['curriculum'])
MAX_BYTES = 10 * 1024 * 1024
MIME = {'.pdf':'application/pdf', '.docx':'application/vnd.openxmlformats-officedocument.wordprocessingml.document', '.txt':'text/plain'}


def assignment_query(db: Session, user_id: int):
    return db.execute(text('''
      SELECT DISTINCT tc.teacher_id,tc.school_id,tc.class_id,tc.subject_id,
        c.class_name,c.grade_level,c.academic_year,s.subject_name
      FROM public.teacher_classes tc
      JOIN public.teachers t ON t.teacher_id=tc.teacher_id AND t.school_id=tc.school_id
      JOIN public.classes c ON c.class_id=tc.class_id AND c.school_id=tc.school_id
      JOIN public.subjects s ON s.subject_id=tc.subject_id
      WHERE t.user_id=:uid
      ORDER BY c.class_name,s.subject_name
    '''), {'uid':user_id}).mappings().all()


def assigned_teacher(db: Session, uid: int, class_id: int, subject_id: int):
    return next((r for r in assignment_query(db, uid) if r['class_id']==class_id and r['subject_id']==subject_id), None)


def owner(db: Session, document_id: int, uid: int):
    return db.execute(text('''
      SELECT d.id,d.title,d.original_filename,d.media_type,d.file_size,d.file_sha256,
        d.created_at,d.status,d.chunk_count,d.extracted_chars,
        d.class_id,d.subject_id,c.class_name,c.grade_level,s.subject_name
      FROM public.teacher_curriculum_documents d
      JOIN public.teachers t ON t.teacher_id=d.teacher_id AND t.school_id=d.school_id
      JOIN public.classes c ON c.class_id=d.class_id AND c.school_id=d.school_id
      JOIN public.subjects s ON s.subject_id=d.subject_id
      WHERE d.id=:did AND t.user_id=:uid AND d.uploaded_by_user_id=:uid
    '''), {'did':document_id,'uid':uid}).mappings().first()


@router.get('/teacher/assignments')
def teacher_assignments(user: User = Depends(roles_allowed('teacher')), db: Session = Depends(get_db)):
    return [dict(row) for row in assignment_query(db,user.user_id)]


@router.get('/teacher/documents')
def teacher_documents(user: User = Depends(roles_allowed('teacher')), db: Session = Depends(get_db)):
    rows = db.execute(text('''
      SELECT d.id,d.title,d.original_filename,d.media_type,d.file_size,d.created_at,
             d.status,d.chunk_count,d.extracted_chars,d.class_id,d.subject_id,
             c.class_name,c.grade_level,s.subject_name
      FROM public.teacher_curriculum_documents d
      JOIN public.teachers t ON t.teacher_id=d.teacher_id AND t.school_id=d.school_id
      JOIN public.classes c ON c.class_id=d.class_id AND c.school_id=d.school_id
      JOIN public.subjects s ON s.subject_id=d.subject_id
      WHERE t.user_id=:uid AND d.uploaded_by_user_id=:uid
      ORDER BY d.created_at DESC,d.id DESC
    '''),{'uid':user.user_id}).mappings().all()
    return [dict(x) for x in rows]


@router.post('/teacher/upload', status_code=201)
async def upload_curriculum(
    class_id: Annotated[int, Form()],
    subject_id: Annotated[int, Form()],
    title: Annotated[str, Form(min_length=3, max_length=240)],
    file: Annotated[UploadFile, File()],
    user: User = Depends(roles_allowed('teacher')),
    db: Session = Depends(get_db),
):
    assignment = assigned_teacher(db,user.user_id,class_id,subject_id)
    if assignment is None:
        raise HTTPException(403,'You are not assigned to teach this subject in this class.')
    filename = Path(file.filename or '').name
    ext = Path(filename).suffix.lower()
    if ext not in MIME:
        raise HTTPException(415,'Only PDF, DOCX and UTF-8 TXT files are allowed.')
    try:
        data = await file.read(MAX_BYTES+1)
    finally:
        await file.close()
    if not data or len(data)>MAX_BYTES:
        raise HTTPException(413,'File is empty or larger than 10 MB.')
    # Magic bytes prevent basic extension spoofing. Parsing also validates the structure.
    if (ext=='.pdf' and not data.startswith(b'%PDF-')) or (ext=='.docx' and not data.startswith(b'PK')):
        raise HTTPException(415,'File content does not match its extension.')
    try:
        pages=extract_pages(data,ext)
        chunks=make_chunks(pages)
    except ValueError as exc:
        raise HTTPException(422,str(exc)) from exc
    if not chunks:
        raise HTTPException(422,'No selectable text was extracted. Scanned PDFs need OCR first.')
    digest=sha256(data).hexdigest()
    exists=db.execute(text('''
       SELECT id FROM public.teacher_curriculum_documents
       WHERE teacher_id=:teacher AND class_id=:class_id AND subject_id=:subject AND file_sha256=:digest
    '''),{'teacher':assignment['teacher_id'],'class_id':class_id,'subject':subject_id,'digest':digest}).scalar_one_or_none()
    if exists:
        raise HTTPException(409,f'This exact file is already uploaded (document {exists}).')
    try:
        docid=db.execute(text('''
            INSERT INTO public.teacher_curriculum_documents
              (school_id,class_id,teacher_id,subject_id,uploaded_by_user_id,
               title,original_filename,media_type,file_size,file_sha256,file_bytes,extracted_chars,chunk_count)
            VALUES (:school,:class_id,:teacher,:subject,:uid,:title,:filename,:media,:size,:digest,:bytes,:chars,:count)
            RETURNING id
        '''),{'school':assignment['school_id'],'class_id':class_id,'teacher':assignment['teacher_id'],
              'subject':subject_id,'uid':user.user_id,'title':title.strip(),'filename':filename,
              'media':MIME[ext],'size':len(data),'digest':digest,'bytes':data,
              'chars':sum(len(c.content) for c in chunks),'count':len(chunks)}).scalar_one()
        for ch in chunks:
            db.execute(text('''INSERT INTO public.teacher_curriculum_chunks
              (document_id,chunk_index,page_number,heading,content)
              VALUES (:did,:idx,:page,:heading,:content)'''),{
              'did':docid,'idx':ch.index,'page':ch.page_number,'heading':ch.heading,'content':ch.content})
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(409,'Document already exists or is invalid.') from exc
    except Exception:
        db.rollback()
        raise
    return {'id':docid,'status':'ready','chunk_count':len(chunks),'file_size':len(data),'title':title.strip()}


@router.get('/teacher/documents/{document_id}/chunks')
def teacher_chunks(document_id:int,limit:int=Query(30,ge=1,le=100),
       user:User=Depends(roles_allowed('teacher')),db:Session=Depends(get_db)):
    document=owner(db,document_id,user.user_id)
    if not document:
        raise HTTPException(404,'Document not found.')
    rows=db.execute(text('''SELECT id,chunk_index,page_number,heading,content FROM public.teacher_curriculum_chunks
        WHERE document_id=:did ORDER BY chunk_index LIMIT :limit'''),{'did':document_id,'limit':limit}).mappings().all()
    return {'document':dict(document),'chunks':[dict(x) for x in rows]}


@router.get('/teacher/documents/{document_id}/download')
def teacher_download(document_id:int,user:User=Depends(roles_allowed('teacher')),db:Session=Depends(get_db)):
    document=owner(db,document_id,user.user_id)
    if not document:
        raise HTTPException(404,'Document not found.')
    data=db.execute(text('SELECT file_bytes FROM public.teacher_curriculum_documents WHERE id=:did'),{'did':document_id}).scalar_one()
    # Filename is not interpolated into Content-Disposition; no header injection.
    return Response(content=bytes(data),media_type=document['media_type'],headers={'Content-Disposition':f'attachment; filename="curriculum-{document_id}{Path(document["original_filename"]).suffix.lower()}"','X-Content-Type-Options':'nosniff'})


@router.get('/student/context')
def student_context(query:str=Query(min_length=2,max_length=250),subject_id:int|None=None,
      user:User=Depends(roles_allowed('student')),db:Session=Depends(get_db)):
    # Exactly the learner's ACTIVE enrolled classes; only ready documents.
    rows=db.execute(text('''
       SELECT d.id AS document_id,d.title,s.subject_name,c.class_name,
              ch.chunk_index,ch.page_number,ch.content,
              ts_rank(ch.search_vector,plainto_tsquery('simple',:q)) AS score
       FROM public.students st
       JOIN public.student_enrollments e ON e.student_id=st.student_id AND e.school_id=st.school_id AND e.ended_at IS NULL
       JOIN public.teacher_curriculum_documents d ON d.class_id=e.class_id AND d.school_id=e.school_id AND d.status='ready'
       JOIN public.teacher_curriculum_chunks ch ON ch.document_id=d.id
       JOIN public.classes c ON c.class_id=e.class_id AND c.school_id=e.school_id
       JOIN public.subjects s ON s.subject_id=d.subject_id
       WHERE st.user_id=:uid AND (:subject IS NULL OR d.subject_id=:subject)
         AND ch.search_vector @@ plainto_tsquery('simple',:q)
       ORDER BY score DESC,d.id,ch.chunk_index LIMIT 6
    '''),{'uid':user.user_id,'q':query,'subject':subject_id}).mappings().all()
    return {'query':query,'chunks':[dict(x) for x in rows]}
