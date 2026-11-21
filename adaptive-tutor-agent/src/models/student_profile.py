from enum import Enum
from pydantic import BaseModel, Field


class SupportCard(str, Enum):
    ADHD = "adhd"
    DYSLEXIA = "dyslexia"
    LOW_CONFIDENCE = "low_confidence"
    TOUGH_COURSEWORK = "tough_coursework"


class StudentProfile(BaseModel):
    student_id: str
    display_name: str = "Student"
    support_cards: list[SupportCard] = Field(default_factory=list)
    learned_baseline: dict[str, float] = Field(
        default_factory=lambda: {"task_minutes": 8.0, "error_limit": 3.0}
    )
    show_audio: bool = False
    share_progress: bool = False
