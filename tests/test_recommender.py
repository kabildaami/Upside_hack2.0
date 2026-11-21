from app.catalog import init_db,get_hobbies
from app.recommender import extract_local,score_hobbies

def test_database_catalog():
    init_db(); hobbies=get_hobbies()
    assert len(hobbies)==40
    assert len(set(h['name'] for h in hobbies))==40
    assert len(set(h['category'] for h in hobbies))>=10
    assert all(len(h['description'])>75 and h['tags'] and h['traits'] for h in hobbies)

def test_tech_recommendation():
    init_db()
    answers=['I enjoy coding, programming and building computer games','I love solving math and logic puzzles','mostly alone','indoors and quiet','I want to create useful apps','no expensive equipment']
    p=extract_local(answers)
    results=score_hobbies(p)
    assert len(results)==5
    assert results==sorted(results,key=lambda h:(-h['score'],h['name']))
    assert any(h['name'] in ('Coding','Robotics','Chess','Digital design') for h in results)

def test_explicit_avoidance():
    init_db()
    p=extract_local(['I like art and design','I draw and paint','alone','indoors','I want to be creative','No dance'])
    assert 'dance' in p['avoid_keywords']
    assert 'Dance' not in [h['name'] for h in score_hobbies(p,40)]

def test_model_profile_clamped():
    from app.recommender import normalize_profile
    p=normalize_profile({'dimensions':{'creative':22,'energetic':-10},'social_mode':'unexpected'})
    assert p['dimensions']['creative']==1 and p['dimensions']['energetic']==0
    assert p['social_mode']=='any'
