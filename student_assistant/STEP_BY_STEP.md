# STEP BY STEP — Windows + PostgreSQL + MCP + LangGraph

## 0. Before you start

Back up `school_db` (for example `pg_dump -U postgres -Fc school_db -f school_db_before_assistant.dump`). Your original schema contains destructive `DROP` commands; **DO NOT run your original 01_schema.sql again** on a database with actual records. Our `02_student_assistant_extension.sql` only creates new `assistant.*` structures and inserts missing hobby catalog labels.

The three course PDFs are **already included** in the ZIP under `data/courses/` and can also be replaced by your own files at `C:\Users\Adam\Desktop\upside_hack\student_assistant\data\courses`.

## 1. Extract folder

Extract `student_assistant` to `C:\Users\Adam\Desktop\upside_hack\student_assistant`. Open PowerShell:

```powershell
cd C:\Users\Adam\Desktop\upside_hack\student_assistant
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
```

Use your existing project Python environment instead of creating a second one if you wish. `mcp>=1.12,<2` is intentionally pinned to the SDK v1 FastMCP interface; do not blindly upgrade to MCP SDK v2, which changes imports. First-time FastEmbed setup downloads the embedding model; allow Internet access once.

## 2. Configure PostgreSQL

Make sure PostgreSQL is running, `school_db` already exists and the `vector` extension is installed in your PostgreSQL instance (many Windows installations need pgvector separately). Update `.env`:

```dotenv
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/school_db
OPENROUTER_API_KEY=YOUR_KEY
OPENROUTER_MODEL=openai/gpt-4o-mini
EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
STUDENT_TIMEZONE=Africa/Tunis
LANGSMITH_TRACING=false
```

Apply the **additive** migration:

```powershell
psql -U postgres -d school_db -f sql\02_student_assistant_extension.sql
psql -U postgres -d school_db -f sql\03_checks.sql
```

If psql isn't recognized use pgAdmin → Query Tool → open/run `sql/02_student_assistant_extension.sql`. If `CREATE EXTENSION vector` fails, install/enable pgvector on that same PostgreSQL instance before proceeding. The database role executing the migration needs CREATE permissions.

## 3. Ingest all three user-provided PDFs

```powershell
python -m scripts.ingest_courses
python -m scripts.test_rag
python -m scripts.inspect_setup
```

Expect `3` documents and nonzero chunks in `assistant.course_chunks`. Each chunk stores its PDF filename and original page number. Rerunning ingestion skips files with the same SHA256. PDF copies reside in the ZIP; ingestion reads those local bytes rather than trying to access this chat.

## 4. Choose an existing student ID and configure a test record

```sql
SELECT s.student_id,u.first_name,u.last_name,sv.grade_level
FROM public.students s JOIN public.users u ON u.user_id=s.user_id
LEFT JOIN public.student_survey sv ON sv.student_id=s.student_id
ORDER BY s.student_id LIMIT 20;
```

For a **synthetic/demo student only**, assuming ID 1 is real:

```powershell
python -m scripts.enable_student_demo --student-id 1 --variant junior --grant-demo-consent
```

This enables learning memory and activity analytics only for the explicitly named demo ID. **Do not apply `--grant-demo-consent` to actual children** without your real guardian/school consent workflow. For an older synthetic student use `--variant senior`; do not attach grade 3 material to a genuine senior school curriculum.

## 5. Discover MCP tools

```powershell
python -m scripts.test_mcp
```

No six-server manual launch is needed. `app/mcp_client.py` uses `MultiServerMCPClient` with six `stdio` subprocess definitions, each running `python -m mcp_servers.<server>_server` with the same Python and working directory. Tools have typed arguments and are discoverable through MCP.

If a subprocess fails, run it directly from the project root to see import problems: `python -m mcp_servers.clock_server` (it will wait silently on stdio until client requests it; Ctrl+C to exit). Never print debug logs to stdio of an MCP server.

## 6. Run the student assistant

```powershell
python -m app --student-id 1 --thread-id student-demo-001 --message "Teach me place value from the Maths Island of Numbers"
python -m app --student-id 1 --thread-id student-demo-001 --message "Make me a maths quiz about place value"
python -m app --student-id 1 --thread-id student-demo-001 --message "1"
python -m app --student-id 1 --thread-id student-demo-001 --message "Plan my lessons next week"
python -m app --student-id 1 --thread-id student-demo-001 --message "Save three goals for next week"
python -m app --student-id 1 --thread-id student-demo-001 --message "Recommend hobbies"
```

The answer `1` submits choice 1 to the most recent unanswered quiz; use 1–4. Some prompts consume OpenRouter credits. Session checkpoints use `AsyncPostgresSaver` with the student/thread key. Durable preferences and progress use separate tables and are available in a new thread. Prompt for a preference: `I prefer visual examples when learning maths.` Then start thread `student-demo-002` and ask for another math explanation; inspect `assistant.learning_memories`.

### Senior test

```powershell
python -m scripts.enable_student_demo --student-id 2 --variant senior --grant-demo-consent
python -m app --student-id 2 --thread-id senior-demo-001 --message "Can we solve linear equations together?"
```

The current edition has only Grade 3 content and therefore intentionally refuses to claim grade-specific coverage for senior lessons. Add senior curriculum and update grade authorization rules before testing actual senior subject tutoring. The Socratic policy and grade separation are implemented, but **end-to-end senior curriculum is not populated**.

## 7. Test pacing events

When integrating the frontend, call `record_activity_event` with a session UUID and actual, consented interaction events. You can create a session from `services.analytics.start_session(student_id,thread_id)`, and end it using `end_session`. Exclude idle/background-tab periods; do not infer mental focus from elapsed time alone. Review `assistant.activity_events`, `assistant.learning_sessions` and `get_pacing_recommendation`.

## 8. LangGraph Studio / LangSmith

```powershell
python -m pip install -U "langgraph-cli[inmem]"
$env:LANGSMITH_TRACING = "true"
$env:LANGSMITH_PROJECT = "Student-Assistant"
langgraph dev --port 2028
```

Open `https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2028` and select `student_assistant`. Example input:

```json
{"student_id":1,"thread_id":"grade3-demo","message":"Quiz me about reading characters and settings in English"}
```

The Studio graph export uses `build_graph()` without a checkpointer because LangGraph manages execution state there; the CLI explicitly uses PostgreSQL checkpoints.

## 9. Offline code verification

```powershell
python -m pytest tests -q
python -m compileall -q app mcp_servers services scripts
```

## 10. Development boundaries / before real pilot

1. Implement OIDC login, server-derived student identity, verified guardian consent and production DB role with enforced RLS (no owner bypass).
2. Implement teacher quiz review and independent answer validation before using generated questions for scoring in real classes.
3. Add approved curriculum for ages 13–18, or keep senior tutoring locked.
4. Add frontend active/idle instrumentation and user feedback; no webcam or surveillance.
5. Apply retention limits, encryption, auditing, rights to view/correct/delete student memory, and human safeguarding protocols.
6. Introduce separate test datasets and LangSmith evaluators for curriculum grounding, quiz correctness, memory isolation and pacing policy.
