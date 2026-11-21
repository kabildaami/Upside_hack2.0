"""Structural tests: no database, embeddings, or remote model needed."""
import pytest
from app.mcp_client import _run_on_server, _config

EXPECTED = {
    "quiz": {"create_quiz_draft", "get_question", "submit_answer"},
    "planning": {"list_study_goals", "create_weekly_goal", "get_hobby_catalog",
                 "get_hobby_questions", "rank_hobbies_from_six_answers"},
    "memory": {"get_student_context", "retrieve_learning_memories", "save_learning_observation"},
    "curriculum": {"search_lessons", "list_course_adventures"},
    "clock": {"get_current_datetime"},
    "analytics": {"get_pacing_recommendation", "record_activity_event", "get_mastery_profile"},
}

@pytest.mark.parametrize("key", sorted(EXPECTED))
def test_mcp_server_registers_tools(key):
    import asyncio
    tools = asyncio.run(_run_on_server(_config()[key]))
    assert set(tools) == EXPECTED[key]
