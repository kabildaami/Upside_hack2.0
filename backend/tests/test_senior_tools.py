from backend.app.agent.senior_culture import CHALLENGES,choose_challenge,verify,normalize

def test_bank_source_grounded():
    assert len(CHALLENGES)>=6
    for c in CHALLENGES:
        assert c['source'].startswith('https://')
        assert c['answer'] not in c['prompt']
        assert len(c['hints'])==2
        assert verify(c,c['answer'])

def test_normalization():
    assert normalize('  Ada-LOVELACE! ')=='ada lovelace'
    assert verify(next(c for c in CHALLENGES if c['key']=='history-ada'),'ada lovelace')
    assert not verify(next(c for c in CHALLENGES if c['key']=='history-ada'),'Isaac Newton')

def test_pick_domain():
    assert choose_challenge('geography')['domain']=='geography'
    assert choose_challenge('nonsense') is None
