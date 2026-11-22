from backend.app.services.rag_student import rank_chunks, extractive_answer, generate_answer

def docs():
    return [
      {'document_id':1,'chunk_index':0,'title':'Math Grade 3','heading':'Place value','content':'A three digit number has hundreds, tens and ones. The number 342 is 3 hundreds, 4 tens, and 2 ones.'},
      {'document_id':1,'chunk_index':1,'title':'Math Grade 3','heading':'Geometry','content':'A triangle has three sides and three corners. A square has four equal sides.'},
    ]

def test_retrieval_finds_topic():
    results=rank_chunks('How do hundreds and tens work?',docs())
    assert len(results)>=1
    assert results[0]['chunk_index']==0

def test_no_overlap_does_not_guess():
    assert rank_chunks('What is photosynthesis?',docs())==[]

def test_extract_quotes_source():
    r=rank_chunks('Tell me about triangles',docs())
    assert 'triangle' in extractive_answer('Tell me about triangles',r).lower()

def test_no_api_key_uses_extractive(monkeypatch):
    monkeypatch.delenv('OPENROUTER_API_KEY',raising=False)
    answer,mode=generate_answer('What is a triangle?',rank_chunks('triangle sides',docs()))
    assert mode=='extractive'
    assert 'triangle' in answer.lower()
