from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["student", "assistant"]
    text: str


class SessionState(BaseModel):
    session_id: str
    student_id: str
    mood: str | None = None
    stress: int = Field(default=0, ge=0, le=10)
    error_streak: int = 0
    active_topic: str | None = None
    focus_minutes: float = 0.0
    messages: list[ChatMessage] = Field(default_factory=list)
