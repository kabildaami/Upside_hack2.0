from datetime import date
from services.rag import chunk_pages
from services.hobbies import recommend,TRAITS
from services.planning import clock
from app.graph import detect_mode,detect_subject

def test_chunk_adventure_heading():
  c=chunk_pages([(3,'Adventure 01 | Reading\nStory Clues\nTODAY I CAN...\nCharacters and setting matter.')]);assert c[0]['adventure_no']==1;assert 'Story Clues' in c[0]['heading'];assert c[0]['page_number']==3

def test_content_overlap():
  x=chunk_pages([(1,'hello world '*500)],limit=400,overlap=50);assert len(x)>4

def test_modes():
  assert detect_mode('quiz me')=='quiz';assert detect_mode('plan next week')=='plan';assert detect_mode('teach me')=='tutor'

def test_subject():
  assert detect_subject('Tell me a history lesson')=='History and geography'

def test_clock():
  a=clock('Africa/Tunis');assert a['weekday'];assert a['next_week_monday'];assert date.fromisoformat(a['next_week_monday']).weekday()==0

def test_hobby_recommendation_traceable():
  r=recommend(['I like computers and technology','I enjoy solving puzzles','I prefer solo','I like digital things','I want to build robots','I have a laptop']);assert len(r)==2; assert 0<=r[0]['score']<=1;assert r[0]['matched_answer_numbers']

def test_hobby_catalog_size():assert len(TRAITS)>=20
