from backend.app.agent.reasoning_grader import canonical, verify_step, source_match, quiz_safe_summary

def test_numeric_step_equivalence_and_nonnumeric_rejection():
    assert verify_step(' 0,30 ', '0.3', 'numeric')
    assert verify_step('-11', '-11', 'numeric')
    assert not verify_step('not a number', '2', 'numeric')
    assert not verify_step('NaN', '0', 'numeric')
    assert not verify_step('Infinity', '0', 'numeric')

def test_exact_step_normalization_and_pedagogic_boundary():
    assert verify_step('2x - 4', '2x-4', 'exact')
    assert not verify_step('x-4', '2x-4', 'exact')
    assert not verify_step('because theorem', '2x-4', 'exact')

def test_grounded_source_match():
    assert source_match('G11-M04 — Limits and continuity', 'G11-M04', [])
    assert source_match('The definition of conditional probability requires nonzero P(B)', 'G11-M08', ['conditional','probability'])
    assert not source_match('A chapter about grammar.', 'G11-M01', ['derivative','function'])

def test_public_payload_does_not_leak_keys_or_hints():
    quiz={'id':9,'title':'Tangent','statement':'Find tangent data','lesson_key':'G11-M05','teacher_explanation':'SECRET'}
    steps=[{'id':101,'position':1,'prompt':'differentiate','expected_answer':'2x-6','hint':'SECRET','xp':8}, {'id':102,'position':2,'prompt':'evaluate','expected_answer':'-2','hint':'SECRET','xp':8}]
    item=quiz_safe_summary(quiz,steps,{1})
    assert item['next_step']['id']==102
    assert item['completed_steps']==1
    assert 'expected_answer' not in str(item)
    assert 'SECRET' not in str(item)
