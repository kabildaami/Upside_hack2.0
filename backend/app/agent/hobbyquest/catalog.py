import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[4] / 'data' / 'hobbyquest_hobbies.sqlite3'
# Each item: name, category, description, tags, traits, environment, social, activity, budget, equipment, accessibility
RAW = [
('Chess','Strategy','Learn openings, tactics, endgames and sportsmanship through thoughtful matches and chess puzzles. Play casually online or join a local club.','strategy,logic,puzzles,competition,indoor','analytical,patient,focused','indoor','both','low','low','chess set or app','Accessible seated activity; visual adaptations available'),
('Coding','Technology','Create websites, simple games, useful scripts and applications while learning computational thinking and debugging. Begin with beginner-friendly projects.','programming,logic,building,computers,problem solving','analytical,curious,creative','indoor','both','low','low','computer or shared device','Screen-based; keyboard and assistive tools may help'),
('Robotics','Technology','Design and program small robots using sensors, motors and simple engineering kits. Explore iterative testing and teamwork.','robots,engineering,building,programming,science','analytical,hands-on,curious','indoor','group','medium','high','robotics kit or club equipment','Club/shared kits lower cost; fine motor adaptations possible'),
('Astronomy','Science','Explore planets, stars and galaxies by observing the sky, tracking constellations and learning how the universe works.','space,stars,observation,science,nature','curious,patient,analytical','both','both','low','low','sky map app; optional binoculars','Many activities are free; night access and transport may vary'),
('Science experiments','Science','Run safe, supervised experiments to test hypotheses, record measurements and understand chemistry, physics and biology.','experiments,lab,discovery,science,hands-on','curious,analytical,hands-on','indoor','both','medium','low','simple household materials and adult guidance','Use age-appropriate, safe protocols only'),
('Environmental volunteering','Community','Join supervised cleanups, biodiversity surveys and conservation projects that improve local environments.','environment,nature,community,impact,teamwork','outdoorsy,social,curious','outdoor','group','medium','low','gloves or organizer-provided materials','Depends on local opportunities and accessible venues'),
('Creative writing','Literature','Write short stories, poems, scripts or fictional worlds; refine your voice through creative prompts and feedback.','writing,stories,poetry,imagination,language','creative,reflective,patient','indoor','solo','low','low','notebook or text editor','Flexible pace; typing, dictation or handwriting'),
('Reading club','Literature','Discover novels and nonfiction, discuss characters and ideas, and share book recommendations with peers.','books,reading,discussion,stories,culture','reflective,curious,social','indoor','group','low','low','library access','Audiobooks and large print can widen access'),
('Learning languages','Culture','Practice a new language through conversations, music, reading and cultural exchange; celebrate progress in communication.','languages,culture,communication,travel,learning','curious,social,patient','both','both','low','low','library or free language resources','Multiple modalities and accessible lessons available'),
('History exploration','Culture','Investigate historical events, artifacts and local heritage through museums, archives, podcasts and research projects.','history,culture,research,museums,stories','curious,reflective,analytical','both','both','low','low','library or museum access','Remote museum tours can be free'),
('Drawing','Visual Arts','Sketch people, environments and imaginary scenes using pencils or digital tools while studying form and composition.','art,sketching,illustration,creative,visual','creative,patient,reflective','indoor','solo','low','low','paper and pencils','Adaptive grips and digital tools are options'),
('Painting','Visual Arts','Explore watercolor, acrylic or other safe media to express ideas using color, texture and composition.','art,paint,color,creative,expression','creative,patient,hands-on','indoor','both','low','medium','paints, brushes and paper','Use non-toxic materials and ventilated space'),
('Photography','Visual Arts','Tell visual stories by learning framing, lighting, portraiture and editing with a phone or camera.','photos,visual,art,exploration,technology','creative,observant,curious','both','both','low','low','phone camera or borrowed camera','Permission and privacy matter when photographing people'),
('Digital design','Visual Arts','Create posters, illustrations and interfaces using accessible graphics tools; practice typography and color theory.','design,graphics,creative,technology,visual','creative,analytical,patient','indoor','both','low','low','computer or shared device','Free design software available'),
('Pottery and ceramics','Crafts','Shape clay by hand or on a wheel, learning texture, form and patience while making useful objects.','clay,sculpture,craf ts,hands-on,creative','creative,hands-on,patient','indoor','both','low','medium','clay; kiln access for fired ceramics','Air-dry clay is an affordable starting point'),
('Origami','Crafts','Fold paper into geometric shapes, animals and decorations, combining precision, spatial thinking and creativity.','paper,crafts,geometry,creative,focus','creative,analytical,patient','indoor','solo','low','low','paper','Can use larger paper or adapted folding aids'),
('DIY electronics','Technology','Build safe low-voltage circuits and sensor projects to understand electricity and prototyping.','circuits,electronics,engineering,hands-on,technology','analytical,hands-on,curious','indoor','both','low','medium','basic low-voltage electronics kit','Adult supervision for age-appropriate electrical safety'),
('Guitar','Music','Learn rhythm, chords and melodies on guitar, practice favorite genres and create original music.','music,guitar,rhythm,performance,creative','creative,patient,expressive','indoor','both','low','medium','guitar or borrowed instrument','Adapted instruments and lessons may help'),
('Piano or keyboard','Music','Explore notes, harmony and improvisation on keys, from simple tunes to original compositions.','music,piano,melody,practice,creative','creative,patient,analytical','indoor','both','low','medium','keyboard or piano access','Digital keyboards offer volume/headphone control'),
('Singing and choir','Music','Develop voice, rhythm and confidence through solo singing or collaborative choir rehearsals.','music,voice,performance,teamwork,expression','expressive,social,creative','indoor','group','medium','low','voice; optional choir','Inclusive choirs and adapted formats possible'),
('Theater','Performing Arts','Act out stories, improvise scenes and develop empathy, communication and public speaking with a theater group.','acting,drama,stories,performance,teamwork','expressive,social,creative','indoor','group','medium','low','theater group or school club','Various speaking and non-speaking roles available'),
('Dance','Performing Arts','Explore movement through contemporary, hip-hop or cultural dance while learning rhythm and choreography.','dance,movement,music,performance,fitness','expressive,energetic,social','indoor','both','high','low','comfortable clothing','Adapted and seated dance options exist'),
('Filmmaking','Media','Plan, shoot and edit short films, practice storytelling, sound and teamwork using accessible video tools.','film,video,stories,creative,technology','creative,social,analytical','both','group','medium','low','phone and free editing software','Protect consent and privacy in recordings'),
('Podcasting','Media','Research topics, interview guests and edit audio episodes while building communication and storytelling skills.','audio,stories,communication,technology,research','expressive,curious,social','indoor','both','low','low','phone microphone and editor','Transcripts improve accessibility'),
('Basketball','Team Sports','Practice dribbling, passing and shooting in a fast-paced team game that builds coordination and collaboration.','basketball,team,sport,fitness,competition','energetic,social,competitive','outdoor','group','high','low','ball and court access','Adapted and wheelchair basketball variants available'),
('Football (soccer)','Team Sports','Learn ball control, passing, positioning and teamwork through casual matches or organized training.','football,soccer,team,sport,competition','energetic,social,competitive','outdoor','group','high','low','ball and field access','Adapted formats available; space and mobility needs vary'),
('Volleyball','Team Sports','Practice serving, setting and teamwork during energetic indoor or outdoor matches.','volleyball,team,sport,coordination','energetic,social,competitive','both','group','high','low','ball and net access','Seated volleyball provides another format'),
('Swimming','Individual Sports','Build water confidence, technique and endurance through supervised pool sessions.','swimming,water,fitness,sport,calm','energetic,focused,patient','indoor','both','high','medium','pool access, swimwear','Requires safe supervision and suitable water accessibility'),
('Cycling','Individual Sports','Explore routes, build endurance and maintain a bicycle safely, from short rides to longer trips.','cycling,bicycle,outdoors,fitness,exploration','energetic,outdoorsy,independent','outdoor','both','high','medium','bike, helmet, safe route','Adaptive cycles and traffic-safe options exist'),
('Running','Individual Sports','Build stamina with gradual running programs, track progress and explore nearby routes.','running,fitness,outdoors,endurance','energetic,independent,focused','outdoor','solo','high','low','suitable shoes','Walking and adapted movement programs possible'),
('Martial arts','Individual Sports','Practice discipline, balance and controlled techniques in a supervised martial arts class.','martial arts,discipline,sport,fitness,focus','energetic,patient,focused','indoor','group','high','medium','club and suitable gear','Choose age-appropriate non-harmful training'),
('Yoga and mobility','Wellness','Explore gentle movement, flexibility and body awareness at a comfortable pace with accessible routines.','yoga,movement,calm,flexibility,wellness','reflective,patient,focused','both','both','low','low','mat optional','Seated and adapted movements available'),
('Hiking','Outdoor Adventure','Explore trails, learn navigation and observe landscapes with appropriate safety planning.','hiking,nature,walking,exploration,adventure','outdoorsy,curious,energetic','outdoor','both','medium','low','comfortable shoes, safe trail','Trail accessibility and support vary'),
('Birdwatching','Nature','Identify birds by sight and sound, keep observation notes and explore local ecosystems.','birds,nature,observation,science,outdoors','observant,patient,outdoorsy','outdoor','both','low','low','notebook; binoculars optional','Can observe from windows or accessible routes'),
('Gardening','Nature','Grow herbs, vegetables or flowers while learning about ecosystems, soil and seasonal care.','plants,garden,nature,hands-on,environment','patient,outdoorsy,hands-on','both','both','medium','low','seeds, container, soil','Indoor pots and raised beds support accessibility'),
('Cooking','Life Skills','Make age-appropriate recipes, learn nutrition basics and explore culinary traditions through safe food preparation.','food,recipes,culture,creative,hands-on','creative,hands-on,curious','indoor','both','medium','low','kitchen access and adult supervision','Adapt tools and recipes to individual needs'),
('Baking','Life Skills','Create breads, pastries and desserts while learning measurement, chemistry and planning.','baking,food,recipes,precision,creative','patient,hands-on,creative','indoor','both','medium','low','kitchen and ingredients','Adult supervision for ovens and hot equipment'),
('Debate club','Communication','Research arguments, practice respectful disagreement and present ideas confidently with peers.','debate,public speaking,logic,communication,teamwork','analytical,social,expressive','indoor','group','low','low','club or discussion group','Written and asynchronous debate options possible'),
('Board games','Strategy','Play cooperative and strategic tabletop games to develop planning, negotiation and social connection.','games,strategy,teamwork,logic,fun','social,analytical,playful','indoor','group','low','low','borrowed or printable games','Accessible editions and large print available'),
('Community service','Community','Volunteer for supervised local projects such as tutoring, food drives or community events to build practical teamwork.','volunteering,community,helping,teamwork,impact','social,empathetic,hands-on','both','group','medium','low','local supervised opportunities','Choose safe, accessible age-appropriate projects'),
]

DIMENSIONS = ['creative','analytical','energetic','social','outdoorsy','reflective','hands-on','expressive','patient','curious','competitive','focused','independent','observant','empathetic','playful']

def get_connection():
    DB_PATH.parent.mkdir(parents=True,exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c=get_connection()
    c.execute('''CREATE TABLE IF NOT EXISTS hobbies (
      id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL, category TEXT NOT NULL,
      description TEXT NOT NULL, tags TEXT NOT NULL, traits TEXT NOT NULL,
      environment TEXT NOT NULL, social_mode TEXT NOT NULL,
      physical_intensity TEXT NOT NULL, estimated_cost TEXT NOT NULL,
      equipment TEXT NOT NULL, accessibility_notes TEXT NOT NULL)''')
    c.execute('CREATE INDEX IF NOT EXISTS idx_hobbies_category ON hobbies(category)')
    for index,item in enumerate(RAW,1):
        name,cat,desc,tags,traits,env,social,activity,cost,equip,access=item
        c.execute('''INSERT OR REPLACE INTO hobbies VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
                  (index,name,cat,desc, tags.replace('craf ts','crafts'),traits,env,social,activity,cost,equip,access))
    c.commit(); c.close()

def get_hobbies():
    c=get_connection()
    result=[dict(r) for r in c.execute('SELECT * FROM hobbies ORDER BY id')]
    c.close()
    for r in result:
        r['tags']=[s.strip() for s in r['tags'].split(',')]
        r['traits']=[s.strip() for s in r['traits'].split(',')]
    return result

if __name__=='__main__':
    init_db(); print('Seeded',len(get_hobbies()),'hobbies into',DB_PATH)
