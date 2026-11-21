# Adaptive Tutor Agent

A privacy-preserving tutoring backend and React interface that adapts presentation to student-selected support preferences. It does not diagnose disabilities or infer them from databases.

## Setup

```powershell
cd adaptive-tutor-agent
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -e ".[dev]"
Copy-Item .env.example .env
uvicorn src.main:app --reload
```

Start the interface:

```powershell
cd frontend
npm install
npm run dev
```

## Privacy and identification

The database stores only an account ID and preferences the student explicitly chooses. Optional institution data may supply a `student_id`, course, or accommodations list, but the agent treats those fields as unverified preferences unless the student confirms them. It never writes diagnostic labels or peer rankings.
