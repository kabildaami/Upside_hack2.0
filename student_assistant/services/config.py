import os
from pathlib import Path
from dotenv import load_dotenv
ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT.parent / '.env')  # shared parent .env if present
load_dotenv(ROOT / '.env', override=True)
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/school_db')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY','')
OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL','openai/gpt-4o-mini')
EMBED_MODEL = os.getenv('EMBED_MODEL','sentence-transformers/all-MiniLM-L6-v2')
STUDENT_TIMEZONE = os.getenv('STUDENT_TIMEZONE','Africa/Tunis')
