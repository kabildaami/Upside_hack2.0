import pytest
from backend.app.agent.hobby_recommender import CATALOG, QUESTIONS,question_for,validate_answer,summarize_and_rank

def test_catalog():
    assert len(CATALOG)==20 and len(QUESTIONS)==6

def test_all_six_answers():
    ids=['solve','lab','master','digital','strategy','device']
    ranked=summarize_and_rank(ids)
    assert len(ranked['top_two'])==2
    assert ranked['completed_questions']==6
    assert ranked['top_two'][0]['score'] >= ranked['top_two'][1]['score']
    assert ranked['top_two'][0]['evidence']
    assert ranked['summary']

def test_invalid_response():
    with pytest.raises(ValueError):validate_answer(1,'not-an-option')
    with pytest.raises(ValueError):summarize_and_rank(['create'])

def test_explanations_reference_selected_answers():
    ids=['create','studio','make','digital','story','lowcost']
    ranked=summarize_and_rank(ids)
    labels={validate_answer(i,x)['label'] for i,x in enumerate(ids)}
    assert all(ev['response'] in labels for row in ranked['top_two'] for ev in row['evidence'])
