from fastapi import APIRouter
from pydantic import BaseModel

from src.models.student_profile import StudentProfile, SupportCard
from src.storage.profile_repo import ProfileRepo


router = APIRouter(prefix="/auth", tags=["auth"])
repo: ProfileRepo


class SignupRequest(BaseModel):
    student_id: str
    display_name: str = "Student"
    support_cards: list[SupportCard] = []


@router.post("/signup")
def signup(payload: SignupRequest):
    profile = StudentProfile(
        student_id=payload.student_id,
        display_name=payload.display_name,
        support_cards=payload.support_cards,
    )
    return repo.upsert(profile)
