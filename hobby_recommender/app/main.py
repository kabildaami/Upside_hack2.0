from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from .catalog import init_db, get_hobbies
from .recommender import QUESTIONS,extract_preferences,score_hobbies

BASE = Path(__file__).resolve().parents[1]

# Load shared environment first
load_dotenv(BASE.parent / ".env")

# Optional project-specific environment
load_dotenv(BASE / ".env", override=True)
BASE=Path(__file__).resolve().parents[1]
@asynccontextmanager
async def lifespan(app:FastAPI):
    init_db()
    yield
app=FastAPI(title='Hobby Discovery API',version='1.0',lifespan=lifespan)
class QuizSubmission(BaseModel):
    answers:list[str]=Field(min_length=6,max_length=6)
@app.get('/')
def home():return FileResponse(BASE/'static'/'index.html')
@app.get('/api/questions')
def questions():return {'questions':QUESTIONS}
@app.get('/api/hobbies')
def hobbies():return {'count':len(get_hobbies()),'hobbies':get_hobbies()}
@app.post('/api/recommend')
async def recommend(submission:QuizSubmission):
    answers=[a.strip() for a in submission.answers]
    if any(not a or len(a)>1200 for a in answers):
        raise HTTPException(422,'Each answer must be between 1 and 1200 characters.')
    profile,method=await extract_preferences(answers)
    return {'recommendations':score_hobbies(profile,5),'profile':profile,'extraction_method':method,
            'note':'Exploratory matches, not personality tests or fixed labels. You can choose any hobby.'}
@app.get('/health')
def health():return {'status':'ok'}
