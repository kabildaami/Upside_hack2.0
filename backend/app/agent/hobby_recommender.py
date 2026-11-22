"""EduNova Senior hobby recommender: six interpretable choices, top two, with evidence.
No external model or personal profiling required. Replace ranking here to plug in the
original hobby engine later while preserving the JSON/API contract.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import TypedDict

class Choice(TypedDict):
    id: str
    label: str
    tags: list[str]

# Each dimension is a non-sensitive activity preference, not a mental-health label.
QUESTIONS = [
    {"id":"activity", "title":"What would you enjoy doing on a free afternoon?", "options":[
        {"id":"create","label":"Make or design something","tags":["creative","hands_on"]},
        {"id":"solve","label":"Solve a challenging puzzle","tags":["logic","technical"]},
        {"id":"move","label":"Be active or explore outdoors","tags":["active","outdoors"]},
        {"id":"connect","label":"Work with or help other people","tags":["social","community"]}]},
    {"id":"environment","title":"Which environment feels most appealing?", "options":[
        {"id":"nature","label":"Nature, plants and open spaces","tags":["outdoors","nature"]},
        {"id":"studio","label":"A creative studio or quiet workshop","tags":["creative","hands_on"]},
        {"id":"library","label":"A library or quiet study space","tags":["reading","reflection"]},
        {"id":"lab","label":"A technology lab or makerspace","tags":["technical","logic"]}]},
    {"id":"motivation","title":"What makes an activity satisfying?", "options":[
        {"id":"learn","label":"Discovering something new","tags":["discovery","reading"]},
        {"id":"make","label":"Creating something I can share","tags":["creative","hands_on"]},
        {"id":"master","label":"Improving a skill through practice","tags":["logic","discipline"]},
        {"id":"help","label":"Making a useful difference","tags":["community","social"]}]},
    {"id":"format","title":"What kind of activity format fits you best?", "options":[
        {"id":"solo","label":"Independent and self-paced","tags":["reflection","reading"]},
        {"id":"team","label":"Small group collaboration","tags":["social","community"]},
        {"id":"physical","label":"Movement and practical action","tags":["active","hands_on"]},
        {"id":"digital","label":"Digital tools or building things","tags":["technical","creative"]}]},
    {"id":"challenge","title":"Which challenge would you choose?", "options":[
        {"id":"strategy","label":"Find a clever strategy","tags":["logic","discipline"]},
        {"id":"story","label":"Tell a story or express an idea","tags":["creative","reading"]},
        {"id":"discover","label":"Investigate a mystery or new place","tags":["discovery","outdoors"]},
        {"id":"lead","label":"Bring people together around a cause","tags":["community","social"]}]},
    {"id":"weekend","title":"What is realistic for you to try next week?", "options":[
        {"id":"lowcost","label":"Something using simple materials at home","tags":["reading","creative","reflection"]},
        {"id":"outside","label":"A walk or outdoor activity","tags":["outdoors","active","nature"]},
        {"id":"device","label":"An activity using a computer or phone","tags":["technical","logic"]},
        {"id":"club","label":"An activity with friends or a local group","tags":["social","community","discipline"]}]}]

# 20 names match the seeded school hobbies table. Descriptions are authored suggestions,
# not asserted properties about any student. Each has explainable interest dimensions.
CATALOG = [
 ("Sports", "Move, practise a skill and enjoy friendly physical challenges.", ["active","discipline","social"]),
 ("Music", "Explore rhythm, instruments, singing or composing.", ["creative","discipline","social"]),
 ("Reading", "Discover stories, ideas and perspectives through books.", ["reading","reflection","discovery"]),
 ("Video games", "Explore interactive worlds and strategy in balanced sessions.", ["technical","logic","creative"]),
 ("Programming", "Build small applications by solving practical problems.", ["technical","logic","hands_on"]),
 ("Drawing / art", "Express ideas through sketches, illustration and other visual media.", ["creative","hands_on","reflection"]),
 ("Travel", "Explore cultures and places through planned visits or local discoveries.", ["outdoors","discovery","social"]),
 ("Movies / series", "Explore stories, cinematography and thoughtful film discussion.", ["creative","reflection","reading"]),
 ("Volunteering", "Contribute to useful projects and help others in your community.", ["community","social","hands_on"]),
 ("Robotics", "Design and test mechanisms and simple electronic projects.", ["technical","logic","hands_on"]),
 ("Photography", "Capture and develop a visual point of view.", ["creative","outdoors","discovery"]),
 ("Creative writing", "Create stories, poems or personal creative projects.", ["creative","reading","reflection"]),
 ("Chess", "Build strategic thinking through games and puzzles.", ["logic","discipline","reflection"]),
 ("Cooking", "Experiment with recipes and practical creative skills.", ["hands_on","creative","community"]),
 ("Gardening", "Care for plants and learn how nature changes over time.", ["nature","outdoors","hands_on"]),
 ("Debate", "Practice evidence-based arguments and listening to other views.", ["logic","social","reading"]),
 ("Astronomy", "Explore the night sky, science and big questions.", ["discovery","logic","nature"]),
 ("Hiking", "Discover trails and landscapes while staying active.", ["outdoors","active","nature"]),
 ("Digital design", "Create visual projects using digital tools.", ["creative","technical","hands_on"]),
 ("Learning languages", "Explore communication, cultures and new vocabulary.", ["reading","social","discovery"])
]
assert len(CATALOG)==20

def question_for(index:int)->dict:
    if not 0 <= index < len(QUESTIONS): raise ValueError('Question index must be 0..5')
    return {k:v for k,v in QUESTIONS[index].items()}

def validate_answer(question_index:int, option_id:str)->dict:
    q=question_for(question_index)
    option=next((o for o in q['options'] if o['id']==option_id),None)
    if option is None: raise ValueError('Invalid option for this question')
    return option

def summarize_and_rank(answer_ids:list[str])->dict:
    if len(answer_ids)!=6: raise ValueError('Six answers are required')
    selected=[validate_answer(i,opt) for i,opt in enumerate(answer_ids)]
    interests={}
    for i,choice in enumerate(selected):
        for tag in choice['tags']: interests[tag]=interests.get(tag,0)+1
    weighted=[]
    for name,description,tags in CATALOG:
        matching=[(i,choice['label'],[tag for tag in choice['tags'] if tag in tags]) for i,choice in enumerate(selected)]
        evidence=[{'question':i+1,'response':label,'shared_preferences':overlap} for i,label,overlap in matching if overlap]
        # Count independent question support rather than repetitive keywords. Max 6 matches.
        evidence_count=len(evidence)
        score=round(100*evidence_count/6)
        weighted.append({'hobby':name,'description':description,'score':score,'matched_responses':evidence_count,'evidence':evidence,'why':('Matched your choices about '+', '.join(e['response'].lower() for e in evidence[:3])+'.') if evidence else 'Exploration option.'})
    weighted.sort(key=lambda x:(-x['matched_responses'],-sum(len(e['shared_preferences']) for e in x['evidence']),x['hobby']))
    top=weighted[:2]
    dominant=sorted(interests.items(),key=lambda x:(-x[1],x[0]))[:3]
    summary='Across six choices, you preferred '+', '.join(t for t,_ in dominant)+'. These suggestions are starting points, not fixed labels.'
    return {'summary':summary,'top_two':top,'completed_questions':6,'catalog_size':len(CATALOG)}
