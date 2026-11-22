"""Senior coach should answer when authorized RAG retrieval finds no passages."""
import asyncio
from unittest.mock import patch
from backend.app.agent import senior_graph


def test_senior_general_chat_without_course_chunks():
    observed={}
    async def fake_model(messages):
        observed['messages']=messages
        return 'Hello! What would you like to learn today?'
    with patch.object(senior_graph,'_openrouter',fake_model):
        result=asyncio.run(senior_graph.coach_node({'question':'hi','evidence':[],'weekly_plan':[],'history':[]}))
    assert result['status']=='answered'
    assert result['answer'].startswith('Hello')
    assert '(none)' in observed['messages'][0]['content']


def test_senior_plan_still_uses_verified_plan():
    result=asyncio.run(senior_graph.coach_node({'question':'my weekly plan','evidence':[],'weekly_plan':[]}))
    assert result['status']=='no_plan'
