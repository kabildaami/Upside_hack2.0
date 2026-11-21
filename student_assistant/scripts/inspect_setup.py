from pathlib import Path
from services.config import DATABASE_URL,OPENROUTER_API_KEY,ROOT
from services.db import query

def main():
    print('OpenRouter key configured:',bool(OPENROUTER_API_KEY))
    try:
        result=query('SELECT current_database() AS database, (SELECT count(*) FROM assistant.course_documents) AS documents, (SELECT count(*) FROM assistant.course_chunks) AS chunks',fetch='one')
        print('Database:',result)
        print('Students:',query('SELECT student_id FROM public.students ORDER BY student_id LIMIT 15'))
    except Exception as e:
        print('Database check failed:',type(e).__name__,str(e)[:300])
    for p in sorted((ROOT/'data'/'courses').glob('*.pdf')):print('PDF:',p.name)
if __name__=='__main__':main()
