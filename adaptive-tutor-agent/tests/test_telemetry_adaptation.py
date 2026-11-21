from src.adaptation.telemetry_tracker import update_baseline
from src.models.session_state import SessionState
from src.models.student_profile import StudentProfile


def test_successful_work_gradually_increases_task_baseline():
    profile = StudentProfile(student_id="student")
    state = SessionState(session_id="test", student_id="student")
    original = profile.learned_baseline["task_minutes"]
    updated = update_baseline(
        profile,
        state,
        elapsed_minutes=10,
        hints_used=0,
        mistakes=1,
    )
    assert updated.learned_baseline["task_minutes"] > original
