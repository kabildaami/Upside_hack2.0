"""Transparent six-answer recommendations using a fixed catalog.
No hidden sensitive profiling; explanations cite the student's answers.
"""
TRAITS={
'Sports':{'active','team'},'Music':{'creative','solo'},'Reading':{'quiet','stories'},
'Video games':{'digital','puzzles'},'Programming':{'digital','puzzles'},
'Drawing / art':{'creative','quiet'},'Travel':{'outdoors','explore'},
'Movies / series':{'stories','quiet'},'Volunteering':{'team','helping'},
'Robotics':{'digital','building'},'Photography':{'creative','explore'},
'Creative writing':{'creative','stories'},'Chess':{'puzzles','quiet'},
'Cooking':{'building','creative'},'Gardening':{'outdoors','quiet'},
'Debate':{'team','stories'},'Astronomy':{'explore','quiet'},
'Hiking':{'active','outdoors'},'Digital design':{'digital','creative'},
'Learning languages':{'stories','explore'}
}
QUESTIONS=[
 'Do you enjoy creating things, solving puzzles, or physical activities?',
 'Do you prefer working on your own or together with others?',
 'Are you interested in computers and technology?',
 'Do you like exploring outdoors or reading stories?',
 'Would you rather build something or help people?',
 'What are the time, access, or budget limits for your new hobby?'
]
WORDS={'creative':('create','art','draw','music','design','write'),
'puzzles':('puzzle','logic','solve','chess','math'),
'active':('sport','run','move','active','exercise'),
'team':('team','friend','group','together'),
'solo':('alone','solo','myself'),
'digital':('tech','computer','digital','program','game'),
'outdoors':('outside','outdoor','nature','walk'),
'explore':('discover','explore','travel','learn'),
'stories':('story','read','book','language'),
'building':('build','make','construct','robot'),
'helping':('help','volunteer','care'),
'quiet':('quiet','calm','relax')}

def recommend(answers:list[str],top_k=2):
    if len(answers)!=6:raise ValueError('Exactly six answers are required')
    text=' '.join(answers).lower()
    matches={trait:[i+1 for i,a in enumerate(answers) if any(w in a.lower() for w in words)] for trait,words in WORDS.items()}
    result=[]
    for hobby,traits in TRAITS.items():
        hits=sorted({i for trait in traits for i in matches[trait]})
        score=round((len(hits)+0.1)/6,3)
        reason=('Matches your answers '+', '.join(f'#{i}' for i in hits) if hits else 'No clear match in your answers')
        result.append({'hobby':hobby,'score':score,'reason':reason,'matched_answer_numbers':hits})
    return sorted(result,key=lambda r:(-r['score'],r['hobby']))[:top_k]
