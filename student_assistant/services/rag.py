import re
from .db import query
from .embeddings import embed

def chunk_pages(pages, limit=1400, overlap=150):
    """PDF-page-aligned chunks with adventure heading carried forward."""
    results=[]; adventure=None; heading=None
    for page_num,text in pages:
        m=re.search(r'(?im)^\s*(?:ADVENTURE|Adventure)\s+(\d+)\b[^\n]*\n([^\n]+)',text)
        if m:
            adventure=int(m.group(1)); heading=m.group(2).strip()
        text=re.sub(r'\s+',' ',text).strip()
        if not text: continue
        start=0
        while start<len(text):
            stop=min(start+limit,len(text))
            if stop<len(text):
                space=text.rfind(' ',start+limit//2,stop)
                if space>start: stop=space
            results.append({'page_number':page_num,'adventure_no':adventure,'heading':heading,'content':text[start:stop]})
            if stop==len(text): break
            start=max(start+1,stop-overlap)
    return results

def search_curriculum(subject:str, question:str, limit:int=4):
    limit=max(1,min(limit,8));
    # Hybrid ranking: lexical FTS for precise topic terms; cosine distance for paraphrases.
    vector=embed(question)
    vec='['+','.join(str(float(x)) for x in vector)+']'
    rows=query('''SELECT c.id, d.filename,d.subject,c.page_number,c.adventure_no,c.heading,
        c.content, (1 - (c.embedding <=> %s::vector)) AS similarity,
        ts_rank(c.content_tsv, plainto_tsquery('english', %s)) AS lexical
      FROM assistant.course_chunks c JOIN assistant.course_documents d ON d.id=c.document_id
      WHERE d.subject= %s AND d.grade_level='3rd primary' AND c.embedding IS NOT NULL
      ORDER BY ((1-(c.embedding <=> %s::vector))*0.8 + ts_rank(c.content_tsv,plainto_tsquery('english',%s))*0.2) DESC
      LIMIT %s''',(vec,question,subject,vec,question,limit))
    return rows

def list_lessons(subject):
    return query('''SELECT DISTINCT c.adventure_no,c.heading,d.filename FROM assistant.course_chunks c
      JOIN assistant.course_documents d ON d.id=c.document_id WHERE d.subject=%s AND c.adventure_no IS NOT NULL
      ORDER BY c.adventure_no,c.heading,d.filename''',(subject,))
