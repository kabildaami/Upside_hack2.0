from src.models.agent_response import AgentResponse
from src.models.session_state import SessionState
from src.models.student_profile import StudentProfile

from .card_merger import load_merged_rules
from .conflict_resolver import resolve_conflicts


def assemble_prompt(
    profile: StudentProfile,
    state: SessionState,
    user_message: str,
) -> tuple[str, AgentResponse]:
    rules = resolve_conflicts(load_merged_rules(profile.support_cards), state)
    accessibility = profile.support_cards
    show_audio = profile.show_audio or "dyslexia" in [card.value for card in accessibility]
    task_size = "small" if "adhd" in [card.value for card in accessibility] or state.mood in {"tired", "stressed"} else "medium"
    timer = False if "dyslexia" in [card.value for card in accessibility] or state.mood in {"tired", "stressed"} else True

    system_prompt = (
        "You are a supportive tutoring agent. Do not diagnose, label, or imply "
        "a medical disability. Never compare the student with peers. "
        "Follow these active support rules:\n- " + "\n- ".join(rules)
        if rules
        else "You are a supportive tutoring agent. Be clear, encouraging, and nonjudgmental."
    )
    ui = AgentResponse(
        text="",
        show_audio=show_audio,
        task_size=task_size,
        timer=timer,
    )
    system_prompt += f"\nStudent request: {user_message}"
    system_prompt += f"\nSession mood: {state.mood or 'not specified'}."
    return system_prompt, ui
