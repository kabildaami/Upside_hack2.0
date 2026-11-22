"""Regression tests for ordinary messages while a quiz remains selected.

The graph module is loaded with a tiny LangGraph import shim when LangGraph is
not installed in the test environment. This tests the actual business logic.
"""
from __future__ import annotations
import importlib
import sys
import types
from unittest.mock import patch


def load_graph():
    try:
        import langgraph.graph
    except ImportError:
        pkg=types.ModuleType('langgraph')
        graph_pkg=types.ModuleType('langgraph.graph')
        graph_pkg.StateGraph=object
        graph_pkg.START='start'
        graph_pkg.END='end'
        with patch.dict(sys.modules, {'langgraph':pkg,'langgraph.graph':graph_pkg}):
            sys.modules.pop('backend.app.agent.graph',None)
            module=importlib.import_module('backend.app.agent.graph')
        return module
    return importlib.import_module('backend.app.agent.graph')


def test_generic_conversation_does_not_activate_quiz_guard():
    graph=load_graph()
    for question in ('hi', 'Explain multiplication', 'Tell me a story', 'How do plants grow?'):
        state={'question':question,'active_quiz':{'prompt':'What is 3 × 4?'},'intent':'tutor'}
        assert graph.choose_tool(state)=='retrieve',question


def test_quiz_specific_requests_remain_protected():
    graph=load_graph()
    for question in ('Give me the answer to this question', 'Solve this quiz', 'Give me a hint', 'Which option is correct?'):
        state={'question':question,'active_quiz':{'prompt':'What is 3 × 4?'},'intent':'tutor'}
        assert graph.choose_tool(state)=='quiz_guard',question
    assert graph.choose_tool({'question':'Give me the answer','active_quiz':None,'intent':'tutor'})=='retrieve'


def test_no_sources_still_calls_general_tutor_and_skips_stale_refusal():
    graph=load_graph()
    request_seen={}
    class FakeResponse:
        def raise_for_status(self):pass
        def json(self):return {'choices':[{'message':{'content':'Multiplication combines equal groups: 3 × 4 = 4 + 4 + 4.'}}]}
    class FakeClient:
        def __init__(self,**kwargs):pass
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def post(self,url,**kwargs):
            request_seen.update(kwargs['json'])
            return FakeResponse()
    state={'question':'Explain multiplication','grade':3,'sources':[],
           'active_quiz':{'prompt':'What is 2 + 2?'},'history':[
               {'role':'assistant','content':"For an active quiz, I won't reveal the solution. Choose a hint."}]}
    with patch.dict(graph.os.environ,{'OPENROUTER_API_KEY':'test-key','OPENROUTER_MODEL':'test-model'}),patch.object(graph.httpx,'Client',FakeClient):
        answer,mode=graph.openrouter_answer(state)
    assert 'equal groups' in answer
    assert mode=='general-tutor'
    assert 'What is 2 + 2?' not in str(request_seen['messages'])
    assert "For an active quiz, I won't reveal" not in str(request_seen['messages'])
    assert request_seen['messages'][-1]['role']=='user'


def test_memory_tool_does_not_duplicate_name():
    graph=load_graph()
    out=graph.planner({'question':'hi','used_tools':['get_time']})
    assert 'used_tools' not in out
    assert graph.memory_tool({'used_tools':['get_time']})['used_tools']==['get_time','conversation_memory']


def test_greeting_has_no_course_citations():
    graph=load_graph()
    assert graph.is_smalltalk('hi!')
    assert graph.is_smalltalk('Good morning')
    assert not graph.is_smalltalk('Explain multiplication')


def test_quiz_list_is_answered_from_verified_data_without_provider():
    graph=load_graph()
    for question in ('what quizes do i have to do?', 'show my quizzes', 'which quizzes are assigned?'):
        assert graph.is_quiz_list_request(question), question
        assert graph.planner({'question':question})['intent']=='quiz_list'
    result=graph.quiz_list_tool({'used_tools':['get_time'], 'available_quizzes':[
        {'subject_name':'Mathematics','lesson_key':'G3-M01','count':3}
    ]})
    assert 'Mathematics' in result['answer'] and '3 question(s)' in result['answer']
    assert result['mode']=='verified-quiz-list'


def test_provider_http_error_is_logged_without_secrets():
    graph=load_graph()
    import httpx
    class FakeClient:
        def __init__(self,**kwargs):pass
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def post(self,url,**kwargs):
            response=httpx.Response(401,request=httpx.Request('POST',url))
            raise httpx.HTTPStatusError('Unauthorized',request=response.request,response=response)
    with patch.dict(graph.os.environ,{'OPENROUTER_API_KEY':'secret-test-key','OPENROUTER_MODEL':'test-model'}),patch.object(graph.httpx,'Client',FakeClient),patch.object(graph.logger,'error') as log:
        answer,mode=graph.openrouter_answer({'question':'hi','grade':3,'sources':[]})
    assert mode=='provider-unavailable'
    assert 'unavailable' in answer
    assert '401' in str(log.call_args)
    assert 'secret-test-key' not in str(log.call_args)
