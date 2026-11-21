# Student Friend Chatbot

A friendly chatbot for students: it listens, supports and gives simple advice.
On serious messages (self-harm, abuse, violence, deep hopelessness) it stops casual advice,
answers with care, encourages a trusted adult or professional, and alerts the parent.

Stack: React (Vite) + FastAPI + PostgreSQL + OpenRouter API.

## Run
1. Database: `createdb friendbot && psql friendbot -f backend/db.sql`
2. Backend: `cd backend && cp .env.example .env` (fill it), then `pip install -r requirements.txt` and `uvicorn src.main:app --reload --port 3000`
3. Frontend: `cd frontend && npm install && npm run dev` -> open http://localhost:5173
4. Log in with a student id (the seed creates student `1`).

## Flow
message -> keyword safety check -> LLM (friend prompt + student profile + memory)
-> if serious (keywords OR LLM flag) -> save alert + short message to parent -> reply

## Before real use
- Replace the student-id login with real authentication (JWT).
- Tell students and parents at sign-up exactly when an alert is sent, and get consent.
- Add the real contact of a school counselor and local help resources (`backend/src/alert.py`).
- The alert contains no conversation text, on purpose.
- Abuse cases: consider alerting a school counselor instead of the parent (the parent may be involved).
