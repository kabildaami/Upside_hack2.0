from backend.app.agent.quiz_tools import grade_answer,valid_quiz_item
from backend.app.agent.time_tools import break_due,current_time

def test_teacher_approved_quiz_schema():
    assert valid_quiz_item(dict(template='multiple_choice',prompt='Which is larger?',options=['4','5'],answer_text='5'))
    assert not valid_quiz_item(dict(template='multiple_choice',prompt='x',options=['4'],answer_text='4'))
    assert valid_quiz_item(dict(template='number_input',prompt='2 + 2',options=[],answer_text='4'))

def test_grading_is_deterministic():
    assert grade_answer('4.0','4','number_input',[])
    assert grade_answer('2,104','2104','number_input',[])
    assert grade_answer('True','True','true_false',['True','False'])
    assert not grade_answer('3','4','number_input',[])

def test_clock_and_break():
    assert not break_due(1799)
    assert break_due(1800)
    c=current_time('Africa/Tunis')
    assert c['timezone']=='Africa/Tunis' and 'T' in c['iso']
