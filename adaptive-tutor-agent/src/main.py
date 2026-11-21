import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import routes_auth, routes_chat, routes_profile
from src.storage.profile_repo import ProfileRepo
from src.storage.session_store import SessionStore


load_dotenv()

app = FastAPI(
    title="Adaptive Tutor Agent",
    description="A student-controlled, privacy-preserving adaptive tutoring service.",
)

origins = [item.strip() for item in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

repo = ProfileRepo(os.getenv("DATABASE_URL", "sqlite:///./adaptive_tutor.db"))
sessions = SessionStore()

routes_auth.repo = repo
routes_profile.repo = repo
routes_chat.repo = repo
routes_chat.sessions = sessions

app.include_router(routes_auth.router)
app.include_router(routes_profile.router)
app.include_router(routes_chat.router)


@app.get("/health")
def health():
    return {"status": "ok"}
