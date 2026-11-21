# Student Assistant — PostgreSQL/pgvector + 6 MCP Services + LangGraph

A local-first prototype for an age-adaptive educational assistant with long-term learning memory. Built for your existing `school_db` containing `public.students`, `public.student_survey`, school/class/teacher relations and student hobby/problem data.

## Contents

- Actual Grade 3 Maya & Leo workbooks: Mathematics, English, History/Geography in `data/courses/`.
- Additive PostgreSQL migration with pgvector, memory, curriculum, quizzes, attempts, study goals, sessions, pacing events and audits.
- Three-PDF ingestion with page/adventure provenance and hybrid PostgreSQL retrieval.
- Six independent local MCP stdio servers: clock, curriculum, memory, quiz, analytics, planning.
- Bounded LangGraph orchestration and two age policies; OpenRouter generation; PostgreSQL durable checkpoints in CLI.
- Transparent consent checks for optional durable memory and pacing analytics.
- Test scripts and exact Windows setup in `STEP_BY_STEP.md`.

**Please read `docs/ARCHITECTURE.md` and `STEP_BY_STEP.md` before installation.**

## Run summary (PowerShell)

```powershell
cd C:\Users\Adam\Desktop\upside_hack\student_assistant
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
# Edit .env; then execute the SQL migration from psql:
psql -U postgres -d school_db -f sql\02_student_assistant_extension.sql
python -m scripts.ingest_courses
python -m scripts.inspect_setup
python -m scripts.test_mcp
python -m app --student-id 1 --message "Teach me place value from maths"
```

Use a REAL existing `student_id` from your database, not necessarily 1. Windows PATH may not contain `psql`; use the PostgreSQL install directory or pgAdmin Query Tool.

### Environment

Copy `.env.example` to `.env` and set `DATABASE_URL`, `OPENROUTER_API_KEY`. If you already keep API credentials in a shared parent `.env`, the loader also searches it. Passwords and keys must never be committed. Default `LANGSMITH_TRACING=false` can be set to true with your existing LangSmith key.

### Known boundaries

- Only Grade 3 courses are included. Senior mode supports its own interaction policy but **requires more appropriate curricula** for academic tutoring/quiz answers.
- Auto-generated quiz answer correctness is not mathematically certified. Use on synthetic users until teacher-reviewed.
- Student focus is **not directly measured**; activity duration and self-feedback are used as proxies for pacing suggestions.
- Consent must be explicitly provided for learning-memory and pacing events. No default consent on real student records.
- CLI student ID is **not production authentication**. Do not expose it publicly.
- The imported PDF files are originals supplied by the user, not generated lesson replacements.
