from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.adaptation.telemetry_tracker import update_baseline
from src.agent.tutor_agent import generate_tutor_response
from src.agent.guardrails import SafetyLevel, safety_check
from src.models.session_state import SessionState
from src.services.alert_service import AlertService
from src.storage.profile_repo import ProfileRepo
from src.storage.session_store import SessionStore


router = APIRouter(prefix="/chat", tags=["chat"])
repo: ProfileRepo
sessions: SessionStore
alerts = AlertService()


class ChatRequest(BaseModel):
    student_id: str
    session_id: str
    message: str


class MoodRequest(BaseModel):
    student_id: str
    session_id: str
    mood: str | None = None
    stress: int = Field(default=0, ge=0, le=10)


class TelemetryRequest(BaseModel):
    student_id: str
    session_id: str
    elapsed_minutes: float = Field(default=0, ge=0)
    hints_used: int = Field(default=0, ge=0)
    mistakes: int = Field(default=0, ge=0)


@router.post("/mood")
def mood(payload: MoodRequest):
    state = sessions.get(payload.session_id, payload.student_id)
    state.mood = payload.mood
    state.stress = payload.stress
    return sessions.update(state)


@router.post("/telemetry")
def telemetry(payload: TelemetryRequest):
    state = sessions.get(payload.session_id, payload.student_id)
    profile = update_baseline(
        repo.get(payload.student_id),
        state,
        elapsed_minutes=payload.elapsed_minutes,
        hints_used=payload.hints_used,
        mistakes=payload.mistakes,
    )
    repo.upsert(profile)
    state.focus_minutes += payload.elapsed_minutes
    state.error_streak = payload.mistakes
    sessions.update(state)
    return {"baseline": profile.learned_baseline}


@router.post("/turn")
async def turn(payload: ChatRequest):
    profile = repo.get(payload.student_id)
    state = sessions.get(payload.session_id, payload.student_id)
    sessions.append_message(state, "student", payload.message)

    safety = safety_check(payload.message)
    if safety.level == SafetyLevel.SERIOUS:
        alerts.create_serious_alert(
            payload.student_id,
            payload.session_id,
            safety.reason or "Possible serious safety concern",
        )
        text = (
            "I’m really glad you told me. You deserve immediate support, not to face "
            "this alone. Please contact someone you trust now—a parent, guardian, "
            "teacher, counselor, or emergency service—and tell them exactly how you "
            "feel. If you might act on this, call your local emergency number."
        )
        result = {
            "text": text,
            "steps": [],
            "show_audio": profile.show_audio,
            "task_size": "small",
            "timer": False,
            "encouragement": "Stay with someone you trust while you get support.",
            "safety_notice": safety.reason,
            "alerted": True,
        }
    else:
        result = await generate_tutor_response(profile, state, payload.message)

    sessions.append_message(state, "assistant", result["text"])
    return result


@router.get("/alerts/{student_id}")
def list_alerts(student_id: str):
    return {"alerts": alerts.list_for_student(student_id)}
