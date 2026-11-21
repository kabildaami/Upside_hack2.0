from src.models.session_state import SessionState
from src.models.student_profile import StudentProfile


def update_baseline(
    profile: StudentProfile,
    state: SessionState,
    *,
    elapsed_minutes: float,
    hints_used: int,
    mistakes: int,
) -> StudentProfile:
    baseline_task = profile.learned_baseline.get("task_minutes", 8.0)
    baseline_errors = profile.learned_baseline.get("error_limit", 3.0)
    adjustment = 0.1

    if elapsed_minutes >= baseline_task and mistakes <= baseline_errors and hints_used <= 1:
        baseline_task = min(30.0, baseline_task + adjustment * 2)
    elif elapsed_minutes < baseline_task * 0.5 or mistakes > baseline_errors:
        baseline_task = max(3.0, baseline_task - adjustment)

    baseline_errors = max(1.0, baseline_errors * 0.95 if mistakes > baseline_errors else baseline_errors)
    profile.learned_baseline = {
        "task_minutes": round(baseline_task, 2),
        "error_limit": round(baseline_errors, 2),
    }
    return profile
