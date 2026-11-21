import contextlib
import json
from psycopg import connect
from psycopg.rows import dict_row
from .config import DATABASE_URL
@contextlib.contextmanager
def connection():
    with connect(DATABASE_URL, row_factory=dict_row, autocommit=False) as conn:
        yield conn

def query(sql, args=(), fetch='all'):
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql,args)
            if fetch=='all': return cur.fetchall()
            if fetch=='one': return cur.fetchone()
            return None

def require_student(student_id: int):
    if not isinstance(student_id,int) or student_id<=0: raise ValueError('Invalid student_id')
    result=query('SELECT student_id FROM public.students WHERE student_id=%s',(student_id,),fetch='one')
    if not result: raise ValueError('Student not found')
    return student_id

def scalar_json(obj):
    return json.dumps(obj,default=str,ensure_ascii=False)
