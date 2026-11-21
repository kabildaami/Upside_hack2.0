"""Ingest the three included user-supplied Grade 3 PDFs into PostgreSQL/pgvector.
Run after sql/02_student_assistant_extension.sql. Idempotent by SHA256.
"""
import hashlib,re
from pathlib import Path
import fitz
from services.db import connection
from services.embeddings import embed
from services.rag import chunk_pages
ROOT=Path(__file__).resolve().parents[1]
COURSES={
 'Grade_3_Maths_The_Island_of_Numbers.pdf':('Mathematics','Maya & Leo: The Island of Numbers'),
 'Grade_3_English_The_Island_of_Stories.pdf':('English','Maya & Leo: The Island of Stories'),
 'Grade_3_History_Geography_The_Explorer_Island.pdf':('History and geography','Maya & Leo: Explorer Island'),
}
def ingest_one(path:Path,subject:str,title:str):
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    with connection() as conn,conn.cursor() as cur:
        cur.execute('SELECT id FROM assistant.course_documents WHERE file_sha256=%s',(digest,))
        previous=cur.fetchone()
        if previous:return {'file':path.name,'status':'already_ingested','id':previous['id']}
    doc=fitz.open(path)
    pages=[(i+1,page.get_text('text')) for i,page in enumerate(doc)]
    chunks=chunk_pages(pages)
    if not chunks:raise ValueError(f'No extractable text in {path.name}; OCR required')
    # Compute embeddings outside DB lock. FastEmbed downloads its model on initial run.
    for c in chunks:c['embedding']='['+','.join(str(float(x)) for x in embed(c['content']))+']'
    with connection() as conn,conn.cursor() as cur:
        cur.execute('''INSERT INTO assistant.course_documents(filename,file_sha256,title,subject,grade_level,storage_path)
          VALUES(%s,%s,%s,%s,'3rd primary',%s) ON CONFLICT(file_sha256) DO UPDATE SET filename=EXCLUDED.filename
          RETURNING id''',(path.name,digest,title,subject,str(path.resolve())))
        doc_id=cur.fetchone()['id']
        for idx,c in enumerate(chunks):
            cur.execute('''INSERT INTO assistant.course_chunks(document_id,chunk_index,page_number,adventure_no,heading,content,embedding)
              VALUES(%s,%s,%s,%s,%s,%s,%s::vector) ON CONFLICT(document_id,chunk_index) DO NOTHING''',
              (doc_id,idx,c['page_number'],c['adventure_no'],c['heading'],c['content'],c['embedding']))
    return {'file':path.name,'id':doc_id,'chunks':len(chunks),'status':'ingested'}

def main():
    directory=ROOT/'data'/'courses'
    for filename,(subject,title) in COURSES.items():
        path=directory/filename
        if not path.is_file():
            print({'status':'missing','file':str(path)});continue
        print(ingest_one(path,subject,title))
if __name__=='__main__':main()
