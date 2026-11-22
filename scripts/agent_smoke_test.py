"""Run from project root: python -m scripts.agent_smoke_test"""
from sqlalchemy import text
from backend.app.db.session import engine
from backend.app.agent.graph import invoke_tutor
from backend.app.agent.time_tools import current_time
from backend.app.agent.quiz_tools import grade_answer

TABLES=['edunova_weekly_plans','edunova_plan_tasks','edunova_quiz_items','edunova_quiz_attempts','edunova_agent_conversations','edunova_agent_messages','edunova_xp_events','edunova_study_breaks']
with engine.connect() as con:
    print('Connected database:',con.execute(text('select current_database()')).scalar())
    missing=[]
    for name in TABLES:
        value=con.execute(text('SELECT to_regclass(:table)'),{'table':'public.'+name}).scalar()
        print(name,'OK' if value else 'MISSING')
        if not value:missing.append(name)
    if missing:raise SystemExit('Run sql/09_langgraph_agent.sql before continuing!')
print('Current clock:', current_time())
print('Grade answer test:',grade_answer('42','42','number_input',[]))
result=invoke_tutor({'question':'What is my weekly progress?','grade':3,'sources':[],'history':[],'plan':[
    {'completed':True},{'completed':False}]})
print('LangGraph progress test:',result['answer'])
assert '50%' in result['answer']
print('EduNova agent smoke test PASSED')
