from services.rag import search_curriculum
for subject,question in [('Mathematics','place value of a four digit number'),('English','characters and setting in a story'),('History and geography','past present future and timeline')]:
    results=search_curriculum(subject,question,3)
    print('\n',subject,'results:',len(results))
    for r in results:print(r['filename'],'page',r['page_number'],(r['heading'] or '')[:60], 'score',round(float(r['similarity']),3))
