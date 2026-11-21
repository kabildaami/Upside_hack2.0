# Tool inventory and acceptance tests

## Test inputs

All commands are run from the project root. Use existing *fictional/demo student IDs*; substitute `<JUNIOR_ID>` and `<SENIOR_ID>` and leave the brackets out.

| # | Request (in `python -m app --student-id ID --thread-id THREAD --message "..."`) | Expected operation | Verify in PostgreSQL |
|---|---|---|---|
| 1 | `Help me understand place value from the Maths Island of Numbers` | Curriculum search, student memory/context, junior tutoring | `assistant.course_chunks` has citation pages |
| 2 | `Quiz me about English characters and setting` | RAG + OpenRouter-generated 4-option quiz draft | `assistant.quiz_items` has 1 item and source chunk id |
| 3 | `1` after quiz | Stored answer lookup, deterministic grading and concept update | `assistant.quiz_attempts`, `assistant.concept_mastery` |
| 4 | `I prefer visual examples when learning maths` | Explicit preference stored with consent | `assistant.learning_memories` |
| 5 | In NEW thread: `Teach me numbers again` | Loads learning memories from DB | Agent answer uses explicitly saved preference |
| 6 | `Plan my week next week` | Clock MCP + suggested scheduled goals | no automatic writes on preview |
| 7 | `Save three goals for next week` | Clock MCP + create_weekly_goal | `assistant.study_goals` |
| 8 | `Recommend hobbies` | Asks six prompts, accepts 6 numbered answers | Top 2 hobbies with score and cited answer numbers |
| 9 | Senior: `Solve linear equations with me` | Senior policy, refusal of grade 3 curriculum | No false grade-specific citations |
| 10 | `python -m scripts.session_demo --student-id ID` | Session events, break timing, pacing engine | `assistant.activity_events`, `assistant.learning_sessions` |

## Quiz validation boundary

The generator requests a structured answer key and validates that the selected index exists. This **does not establish factual correctness**. For a real teacher-owned learning platform, implement content verification by a separate model with source excerpts, deterministic math validation where possible, and teacher approval before displaying an automatically graded question.

## MCP operational testing

- `python -m scripts.test_mcp`: discovers tools across six stdio servers and calls clock.
- `python -m scripts.test_rag`: searches all three subjects using pgvector + lexical ranking.
- `python -m scripts.inspect_setup`: verifies course rows, database and students.
- `python -m pytest tests -q`: pure offline tests.

## Long-term learning test

1. Enable consent on a synthetic student, then teach/quiz once.
2. Insert an explicit preference statement.
3. Terminate the process.
4. Start a new CLI process **with a different thread ID**.
5. Request a fresh explanation and inspect whether it uses the stored preference and recent mastery records.
6. Verify another student does not receive this student's memory.
7. Revoke learning_memory consent and confirm retrieval returns empty.
8. Review memory records and test archival/redaction workflows before production.

## Time measurement limits

An MCP clock provides wall-clock date/time. It doesn't detect concentration. Focus-span estimates must rely on explicitly reported frontend activity duration, idle detection, task completion and student self-feedback. `scripts.session_demo.py` illustrates data entry. Duration measured for a quiz item does not imply attention or a psychological diagnosis.
