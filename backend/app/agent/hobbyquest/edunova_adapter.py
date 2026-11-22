"""Glue between the uploaded HobbyQuest scoring engine and EduNova storage contract."""
from __future__ import annotations
import re
from .catalog import init_db, get_hobbies
from .recommender import QUESTIONS, extract_preferences, score_hobbies


def question_for(index: int) -> dict:
    if not 0 <= index < len(QUESTIONS):
        raise ValueError('Expected question 0..5')
    q=QUESTIONS[index]
    return {'id':q['id'], 'title':q['title'], 'placeholder':q['placeholder']}


def validate_free_text(value: str) -> str:
    if not isinstance(value,str) or not (2 <= len(value.strip()) <= 1200):
        raise ValueError('Answer must contain between 2 and 1200 characters')
    return value.strip()


def evidence_for(hobby:dict,answers:list[str]) -> list[dict]:
    """Exact phrase-only evidence; do not claim unsupported semantic links.

    An answer is always shown as its original text. We highlight only explicit
    name/tags mentions, excluding simple negative contexts. Profile-wide traits
    are explained separately by the original engine.
    """
    terms=[hobby['name'].lower(),*hobby['tags']]
    terms=sorted({t.strip() for t in terms if len(t.strip())>=4},key=len,reverse=True)
    evidence=[]
    for i,answer in enumerate(answers):
        matches=[]
        for term in terms:
            pattern=r'(?<!\w)'+re.escape(term)+r'(?!\w)'
            for m in re.finditer(pattern,answer.lower()):
                preceding=answer[max(0,m.start()-24):m.start()].lower()
                if re.search(r'\b(?:no|avoid|dislike|hate|not|never|without)\s+(?:any\s+)?$',preceding):continue
                matches.append(term)
                break
        evidence.append({'question':i+1,'response':answer,'shared_preferences':matches[:4]})
    return evidence


async def recommend_for_edunova(answers:list[str]) -> dict:
    if len(answers)!=6: raise ValueError('Exactly six answers are required')
    answers=[validate_free_text(x) for x in answers]
    init_db()  # seed original curated 40-hobby catalog on first use
    profile,method=await extract_preferences(answers)
    catalog={h['name']:h for h in get_hobbies()}
    top=score_hobbies(profile,top_k=2)
    recommendations=[]
    for rank,item in enumerate(top,1):
        h=catalog[item['name'] if 'name' in item else item.get('hobby')]
        recommendations.append({'rank':rank,'hobby_name':h['name'], 'score':int(round(item['score'])),
          'description':h['description'], 'reason':'; '.join(item.get('reasons',[])) or 'Matches the interests and practical preferences you expressed.',
          'evidence':evidence_for(h,answers), 'breakdown':item})
    return {'summary':profile['summary'] or 'Six-answer preference profile.', 'extraction_method':method,
       'results':recommendations,'catalog_size':len(catalog),'profile':profile}
