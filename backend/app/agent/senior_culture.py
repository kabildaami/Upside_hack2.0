"""Verified educational facts. Remote lookup is constrained to public allowlisted sources."""
from __future__ import annotations
import random
import httpx

# Curated facts are deliberately small; no LLM authored answer keys.
CHALLENGES = [
 {'key':'history-ada','domain':'history','prompt':'Which mathematician wrote notes describing an algorithm for Charles Babbage’s Analytical Engine?','answer':'Ada Lovelace','accepted':['ada lovelace','augusta ada king'], 'hints':['She worked in 19th-century Britain.','Her collaborator was Charles Babbage.'], 'reason':'Ada Lovelace described an algorithm for Babbage’s proposed machine.','source':'https://www.britannica.com/biography/Ada-Lovelace'},
 {'key':'history-timbuktu','domain':'history','prompt':'Which West African city became famous for scholarship and manuscript libraries under the Mali and Songhai empires?','answer':'Timbuktu','accepted':['timbuktu','tombouctou'], 'hints':['It is in present-day Mali.','Its name begins with T.'], 'reason':'Timbuktu was a significant center of Islamic learning and book culture.','source':'https://whc.unesco.org/en/list/119/'},
 {'key':'geography-atlas','domain':'geography','prompt':'Which mountain range runs through Morocco, Algeria, and Tunisia?','answer':'Atlas Mountains','accepted':['atlas mountains','atlas','atlas mountain range'], 'hints':['It lies in North Africa.','Its name is also used for a collection of maps.'], 'reason':'The Atlas range extends across Morocco, Algeria and Tunisia.','source':'https://www.britannica.com/place/Atlas-Mountains'},
 {'key':'geography-danube','domain':'geography','prompt':'Which major European river flows through Vienna, Bratislava, Budapest, and Belgrade?','answer':'Danube','accepted':['danube','danube river'], 'hints':['Its source is in Germany.','It is Europe’s second-longest river.'], 'reason':'The Danube crosses multiple central and eastern European capitals.','source':'https://www.britannica.com/place/Danube-River'},
 {'key':'economics-inflation','domain':'economics','prompt':'What is the term for a sustained increase in the general price level of goods and services?','answer':'Inflation','accepted':['inflation'], 'hints':['It reduces purchasing power if wages do not keep up.','It begins with the letter I.'], 'reason':'Inflation describes an ongoing rise in the overall price level.','source':'https://www.imf.org/en/Publications/fandd/issues/Series/Back-to-Basics/Inflation'},
 {'key':'economics-opportunity','domain':'economics','prompt':'What is the value of the next best alternative you give up when you make a choice called?','answer':'Opportunity cost','accepted':['opportunity cost'], 'hints':['It is about a trade-off.','Economists call it an opportunity ...'], 'reason':'Opportunity cost captures the benefits forgone from the next-best option.','source':'https://www.britannica.com/money/opportunity-cost'},
]

def choose_challenge(domain='all', exclude=()):
    pool=[c for c in CHALLENGES if (domain=='all' or c['domain']==domain) and c['key'] not in exclude]
    return dict(random.choice(pool)) if pool else None

def normalize(text):
    import re,unicodedata
    s=unicodedata.normalize('NFKD',text.casefold());s=''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+',' ',s).strip()

def verify(challenge,response):
    return normalize(response) in {normalize(x) for x in challenge['accepted']}

async def wikipedia_entity_lookup(term:str):
    """Public encyclopedia search only. No arbitrary URLs / SSRF."""
    async with httpx.AsyncClient(timeout=8,headers={'User-Agent':'EduNovaEducation/0.1 (school educational prototype)'}) as client:
        r=await client.get('https://en.wikipedia.org/w/api.php',params={'action':'query','list':'search','srsearch':term[:100],'srlimit':3,'format':'json'});r.raise_for_status()
    return [{'title':x['title'],'url':'https://en.wikipedia.org/wiki/'+x['title'].replace(' ','_'),'snippet':__import__('re').sub('<[^>]*>','',x.get('snippet',''))} for x in r.json().get('query',{}).get('search',[])]

async def country_lookup(name:str):
    async with httpx.AsyncClient(timeout=8) as client:
        r=await client.get('https://restcountries.com/v3.1/name/'+__import__('urllib.parse',fromlist=['quote']).quote(name[:70],safe=''),params={'fields':'name,capital,region,subregion,languages,population'});r.raise_for_status()
    return [{'name':d.get('name',{}).get('common'),'capital':d.get('capital',[]),'region':d.get('region'),'population':d.get('population'),'source':'https://restcountries.com/'} for d in r.json()[:4]]
