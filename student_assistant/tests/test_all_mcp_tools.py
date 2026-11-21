"""Diagnostic smoke tests for all 17 Student Assistant MCP tools.

Run from the project root:
  python tests/test_all_mcp_tools.py --student-id 1
  python tests/test_all_mcp_tools.py --student-id 1 --write

--write creates demo test records and one quiz attempt. Only use a demo student.
"""
import argparse
import asyncio
import json
import sys
import time
import traceback
import uuid
from pathlib import Path

# Allow execution from tests/ without installing the project package.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.mcp_client import tool_call


SUBJECT = "Mathematics"


def unpack(value):
    """Normalize JSON text/content blocks returned by different MCP adapters."""
    if isinstance(value, dict):
        if "structuredContent" in value:
            return unpack(value["structuredContent"])
        if "content" in value and isinstance(value["content"], list):
            return unpack(value["content"])
        return value
    if isinstance(value, str):
        try:
            return unpack(json.loads(value))
        except (ValueError, TypeError):
            return value
    if isinstance(value, list):
        if value and all(isinstance(x, dict) and "text" in x for x in value):
            return unpack("".join(x["text"] for x in value))
        return value
    # LangChain may return TextContent-like objects.
    if hasattr(value, "content"):
        return unpack(value.content)
    return value


def first_id(payload):
    """Find a returned id in a row, rows, or MCP content wrapper."""
    payload = unpack(payload)
    if isinstance(payload, dict):
        if payload.get("id") is not None:
            return str(payload["id"])
        for key in ("results", "items", "rows", "data"):
            if key in payload:
                found = first_id(payload[key])
                if found is not None:
                    return found
    elif isinstance(payload, list):
        for item in payload:
            found = first_id(item)
            if found is not None:
                return found
    return None


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--student-id", type=int, default=1,
                        help="Existing fictional/demo student in Supabase")
    parser.add_argument("--timeout", type=float, default=75,
                        help="Per-tool timeout in seconds")
    parser.add_argument("--write", action="store_true",
                        help="Also test tools that create database records")
    args = parser.parse_args()

    results = []
    context = {}

    async def check(name, **kwargs):
        print(f"\n▶ {name} | args={str(kwargs)[:250]}", flush=True)
        begin = time.perf_counter()
        try:
            raw = await asyncio.wait_for(tool_call(name, **kwargs), timeout=args.timeout)
            response = unpack(raw)
            elapsed = time.perf_counter() - begin
            # MCP tools sometimes return an error payload rather than raising.
            if isinstance(response, dict) and (response.get("isError") is True):
                raise RuntimeError(f"MCP returned isError=true: {response}")
            print(f"  PASS ({elapsed:.2f}s): {str(response)[:450]}", flush=True)
            results.append((name, "PASS", elapsed, ""))
            return response
        except Exception as exc:
            elapsed = time.perf_counter() - begin
            print(f"  FAIL ({elapsed:.2f}s): {type(exc).__name__}: {exc}", flush=True)
            traceback.print_exc(limit=8)
            results.append((name, "FAIL", elapsed, str(exc)[:120]))
            return None

    async def skipped(name, reason):
        print(f"\n- SKIP {name}: {reason}", flush=True)
        results.append((name, "SKIP", 0, reason))

    sid = args.student_id

    # 1. CLOCK (1 tool)
    clock = await check("get_current_datetime", timezone="Africa/Tunis")
    target_date = clock.get("next_week_monday") if isinstance(clock, dict) else None

    # 2. CURRICULUM (2 tools)
    for subject in ("Mathematics", "English", "History and geography"):
        # Run both tool types on each subject; these are separate invocations, same tool name.
        await check("list_course_adventures", subject=subject)
    chunks = await check("search_lessons", subject=SUBJECT,
                         question="place value tens hundreds", limit=2)
    context["source_chunk_id"] = first_id(chunks)

    # 3. MEMORY (3 tools)
    await check("get_student_context", student_id=sid)
    await check("retrieve_learning_memories", student_id=sid,
                query="", limit=3)  # Empty query avoids an embedding download.
    if args.write:
        await check("save_learning_observation", student_id=sid,
                    category="learning_preference",
                    content="MCP diagnostic: this demo student prefers visual examples.")
    else:
        await skipped("save_learning_observation", "requires --write")

    # 4. QUIZ (3 tools)
    quiz_id = None
    if args.write and context["source_chunk_id"] is not None:
        drafted = await check(
            "create_quiz_draft", student_id=sid, subject=SUBJECT,
            concept="place_value", source_chunk_id=int(context["source_chunk_id"]),
            question="MCP diagnostic: How many tens are in 40?",
            options=["2", "3", "4", "5"], answer_index=2,
            hint="Think in groups of ten.", difficulty=1,
        )
        quiz_id = first_id(drafted)
    else:
        await skipped("create_quiz_draft",
                      "requires --write and successful curriculum retrieval with an id")
    if quiz_id:
        await check("get_question", student_id=sid, quiz_id=quiz_id)
        await check("submit_answer", student_id=sid, quiz_id=quiz_id,
                    selected_index=2, hints_used=0, response_seconds=12)
    else:
        await skipped("get_question", "no quiz id; run with --write")
        await skipped("submit_answer", "no quiz id; run with --write")

    # 5. ANALYTICS (3 tools)
    await check("get_pacing_recommendation", student_id=sid)
    await check("get_mastery_profile", student_id=sid)
    if args.write:
        # A learning session is a required FK for record_activity_event.
        # The packaged MCP tools have no create-session tool, so use the existing
        # application service to make a *demo* session before exercising the MCP.
        try:
            from services.analytics import start_session
            row = await asyncio.to_thread(
                start_session, sid, f"mcp-test-{uuid.uuid4().hex[:10]}", SUBJECT
            )
            session_id = first_id(row)
            if session_id:
                await check("record_activity_event", student_id=sid,
                            session_id=session_id, event_type="activity_completed",
                            duration_seconds=25)
            else:
                await skipped("record_activity_event", "session creation returned no id")
        except Exception as exc:
            print(f"  Session setup failed: {type(exc).__name__}: {exc}")
            await skipped("record_activity_event", "could not create demo session")
    else:
        await skipped("record_activity_event", "requires --write")

    # 6. PLANNING (5 tools)
    await check("list_study_goals", student_id=sid)
    await check("get_hobby_catalog", student_id=sid)
    await check("get_hobby_questions")
    await check("rank_hobbies_from_six_answers", student_id=sid, answers=[
        "I like building puzzles and solving problems.",
        "I enjoy creative drawing and making things.",
        "I prefer a mixture of indoor and outdoor activities.",
        "I like exploring science and technology.",
        "I enjoy collaborating with friends.",
        "I would like to learn coding and robotics.",
    ])
    if args.write and target_date:
        await check("create_weekly_goal", student_id=sid, subject=SUBJECT,
                    goal="MCP diagnostic: practice place value for 10 minutes",
                    target_date=target_date)
    else:
        await skipped("create_weekly_goal", "requires --write and Clock MCP date")

    print("\n" + "=" * 80)
    print("MCP DIAGNOSTIC SUMMARY (17 unique tools; 19 calls if all three subjects run)")
    for name, status, seconds, note in results:
        print(f"{status:4} {seconds:7.2f}s  {name:<34} {note}")
    print("=" * 80)
    passes = sum(x[1] == "PASS" for x in results)
    fails = sum(x[1] == "FAIL" for x in results)
    skips = sum(x[1] == "SKIP" for x in results)
    print(f"PASS: {passes} | FAIL: {fails} | SKIP: {skips}")
    if fails:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
