from fastapi import APIRouter
from pydantic import BaseModel

from src.models.student_profile import StudentProfile, SupportCard
from src.storage.profile_repo import ProfileRepo


router = APIRouter(prefix="/profile", tags=["profile"])
repo: ProfileRepo


class ProfileUpdate(BaseModel):
    display_name: str | None = None
    support_cards: list[SupportCard] | None = None
    show_audio: bool | None = None
    share_progress: bool | None = None


@router.get("/{student_id}")
def get_profile(student_id: str):
    return repo.get(student_id)


@router.patch("/{student_id}")
def update_profile(student_id: str, payload: ProfileUpdate):
    profile = repo.get(student_id)
    updates = payload.model_dump(exclude_unset=True)
    return repo.upsert(profile.model_copy(update=updates))
