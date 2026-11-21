# Student Assistant: 6 local MCP servers (Windows / PowerShell)

This ZIP is a **drop-in overlay**, not a copy of your full application. It implements six real MCP stdio servers using your existing `services.*` functions. The service modules, databases, RAG index, data files, and existing application are **not included**. They are necessary for their corresponding *business operations* to work.

## What is included

| Server module | MCP tools |
| --- | --- |
| `servers.quiz_server` | `create_quiz_draft`, `get_question`, `submit_answer` |
| `servers.planning_server` | `list_study_goals`, `create_weekly_goal`, `get_hobby_catalog`, `get_hobby_questions`, `rank_hobbies_from_six_answers` |
| `servers.memory_server` | `get_student_context`, `retrieve_learning_memories`, `save_learning_observation` |
| `servers.curriculum_server` | `search_lessons`, `list_course_adventures` |
| `servers.clock_server` | `get_current_datetime` |
| `servers.analytics_server` | `get_pacing_recommendation`, `record_activity_event`, `get_mastery_profile` |

## 1. Back up and merge

Unzip into a temporary directory, then copy `servers/`, `config/`, `scripts/` into the root of `student_assistant`. Copy **only** `app/mcp_client.py` after backing up your original `app/mcp_client.py` and reviewing differences. Keep your existing `services/`, database, indexes and `pyproject.toml`. Do **not** overwrite existing tests: merge or rename similarly named test modules if needed. Existing `__init__.py` files need not be replaced. This archive intentionally does not overwrite your real services.

Result:

```text
student_assistant/
  app/
    __init__.py
    mcp_client.py
  servers/
    __init__.py
    quiz_server.py
    planning_server.py
    memory_server.py
    curriculum_server.py
    clock_server.py
    analytics_server.py
  services/                 <-- yours, unchanged
    quiz.py
    planning.py
    hobbies.py
    student.py
    rag.py
    analytics.py
    db.py
  config/mcp_servers.json
  scripts/check_mcp.py
  tests/test_mcp_registration.py
  tests/test_mcp_clock.py
  requirements-mcp.txt
```

## 2. Create the right virtual environment

PowerShell (from project root):

```powershell
cd C:\Users\Adam\Desktop\upside_hack\student_assistant
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -c "import sys; print(sys.executable)"
python -m pip install -r requirements-mcp.txt
# Install your EXISTING application dependencies as well:
# python -m pip install -r requirements.txt
# or: python -m pip install -e .
```

The interpreter should be under `student_assistant\.venv`, **not** `Agents_In_Practice\.venv`.

**MCP version:** this project deliberately pins the official `mcp` Python package to SDK v1 (`mcp>=1.12,<2`) for `from mcp.server.fastmcp import FastMCP`. SDK v2 moved/renamed this API. Do not mix instructions for v1 and v2.

## 3. Confirm services and data

Run this from project root:

```powershell
python -c "from services.planning import clock; print(clock('Africa/Tunis'))"
```

If this fails, fix your pre-existing `services/` imports/dependencies first. Quiz, memory, analytics and curriculum operations also require their own database or index to be initialized. Discovery should still work because service imports are deferred until a tool is called.

## 4. Verify tools and one actual call

```powershell
python -m scripts.check_mcp
python -m pytest tests/test_mcp_registration.py tests/test_mcp_clock.py -v -s
```

The check starts six local Python subprocesses over MCP stdio, discovers tool names, then calls the clock server. For just one server manually:

```powershell
python -m servers.curriculum_server
```

A stdio server appears idle; that is normal because it waits for JSON-RPC requests on stdin. Press Ctrl+C to stop it. **Never print application debug logs to stdout from an MCP stdio server**; use stderr/logging instead.

## 5. Call the curriculum server from Python

```python
import asyncio
from app.mcp_client import tool_call

async def main():
    lessons = await tool_call(
        "search_lessons",
        subject="Mathematics",
        question="How can I compare two fractions?",
        limit=4,
    )
    print(lessons)

if __name__ == "__main__":
    asyncio.run(main())
```

Run as `python -m YOUR_MODULE` from project root. For a real performance test, run:

```powershell
$env:RUN_CURRICULUM_INTEGRATION = '1'
python -m pytest tests/test_curriculum_speed_example.py -v -s
```

If curriculum is slow, profile `services.rag.search_curriculum` and its index/model startup separately. Increasing timeouts does not fix slowness. First call in the supplied client includes one-time tool discovery; subsequent calls use a cached registry, but each call opens its own process/session.

## 6. Client/server configuration details

`config/mcp_servers.json` maps logical keys to fully qualified Python modules. `app.mcp_client` uses `sys.executable`, `python -m <module>` and sets `PYTHONPATH` to the root. No hardcoded paths or persistent background processes. The client launches and shuts down each subprocess via async context managers.

Call signature: `await tool_call('get_current_datetime', timezone='Africa/Tunis')`. The helper discovers the owning server, then invokes the tool. Do not call with a missing name. Client tool discovery is cached in the Python process, not persisted across restarts.

If you integrate this with an LLM, provide ONLY the tools allowed for the authenticated student, and inject the real `student_id` from server-side authentication. This transport is local, not an authentication boundary. **Your underlying services must enforce identity isolation, teacher approval and consent; docstrings and numeric IDs alone are not access control.** Quiz drafts and memory writes must remain subject to these checks.

## 7. Troubleshooting

- `ModuleNotFoundError: mcp`: `python -m pip install -r requirements-mcp.txt` in the selected venv.
- `ModuleNotFoundError: services`: ensure your `services/` folder exists at the project root and is importable.
- Wrong interpreter: `python -c "import sys; print(sys.executable)"` then reactivate the correct `.venv`.
- `TimeoutError` after `CallToolRequest`: the MCP server answered discovery, but its service function did not return in time; inspect its database, vector retrieval, API calls, and initialization.
- Tool failure after successful discovery: a missing dependency or service-layer error may be raised only when invoking the tool (intentional lazy imports).
- `AnyIO WouldBlock` while timed out: this is the interrupted client waiting for a server response, not proof that the import is broken.
- `pytest collected 0 items`: avoid running `asyncio.run(...)` at import time; wrap in `def test_...():`.
- If the project is on SDK v2 rather than v1, use a separate migration to `MCPServer` and its updated client API; do not combine the versions.

## Important limitations

I did not receive your existing `services/*.py`, database schemas, or course files. I therefore preserved the functions and call signatures provided and cannot verify their behavior, student authorization, output formats, quiz grading, or RAG latency. Tests verify the server-to-client protocol and tool discovery; real data calls require your actual services.
