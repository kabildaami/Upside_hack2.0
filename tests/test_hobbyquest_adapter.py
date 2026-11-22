import asyncio
from backend.app.agent.hobbyquest.edunova_adapter import question_for,validate_free_text,recommend_for_edunova
from backend.app.agent.hobbyquest.agent_tool import hobby_context_text

def test_six_prompts():
    assert [question_for(i)['id'] for i in range(6)] == ['interests','strengths','social','setting','goals','constraints']

def test_input_validation():
    assert validate_free_text('  coding  ') == 'coding'
    for x in ['','a','x'*1201]:
        try: validate_free_text(x)
        except ValueError: pass
        else: assert False

def test_original_catalog_returns_only_two_with_evidence(monkeypatch):
    monkeypatch.delenv('OPENROUTER_API_KEY',raising=False)
    answers=['I enjoy coding and mathematics','I solve logic puzzles','I prefer solo projects','Indoors in a calm space','I want to build creative computer projects','Low budget, avoid team sports']
    result=asyncio.run(recommend_for_edunova(answers))
    assert result['catalog_size']==40
    assert len(result['results'])==2
    assert all(len(r['evidence'])==6 and 0<=r['score']<=100 for r in result['results'])
    assert result['extraction_method'].startswith('local-fallback')

def test_no_fabricated_hobby_memory():
    assert 'No completed' in hobby_context_text({'available':False,'results':[]})
