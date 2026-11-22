"""Read-only tool for EduNova's senior tutor to recall approved HobbyQuest results.

No raw questionnaire answers leave PostgreSQL through this interface.
"""
from sqlalchemy import text

def latest_hobby_discovery(db, student_id: int) -> dict:
    session=db.execute(text("""SELECT id,summary FROM public.senior_hobby_sessions
      WHERE student_id=:sid AND engine_version='hobbyquest_v2' AND status='completed'
      ORDER BY completed_at DESC LIMIT 1"""),{'sid':student_id}).mappings().first()
    if not session:return {'available':False,'results':[]}
    rows=db.execute(text("""SELECT hobby_name,score,reason FROM public.senior_hobby_recommendations
      WHERE session_id=:id ORDER BY rank"""),{'id':session['id']}).mappings()
    return {'available':True,'summary':session['summary'],'results':[dict(r) for r in rows]}

def hobby_context_text(data: dict) -> str:
    if not data.get('available'):
        return 'No completed HobbyQuest discovery yet. Suggest opening the Hobby discovery tool to answer six questions; never invent scores.'
    results='; '.join(f"{r['hobby_name']} ({r['score']}/100 heuristic match): {r['reason']}" for r in data['results'][:2])
    return 'Student-owned completed HobbyQuest session. '+str(data.get('summary',''))[:320]+' Top two: '+results[:750]+'. Scores are exploratory, never probability or proof of ability.'
