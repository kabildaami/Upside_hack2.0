from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.authentication import get_current_user
from app.models.school import School
from app.models.user import User
from pydantic import BaseModel

router = APIRouter(prefix="/schools", tags=["schools"])


class SchoolCreate(BaseModel):
    name: str
    address: str | None = None


class SchoolRead(BaseModel):
    id: str
    name: str
    address: str | None = None

    model_config = {"from_attributes": True}


@router.post("", response_model=SchoolRead, status_code=status.HTTP_201_CREATED)
def create_school(
    payload: SchoolCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> School:
    if current_user.role != "director":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Director role required")
    school = School(name=payload.name, address=payload.address)
    db.add(school)
    db.commit()
    db.refresh(school)
    return school


@router.get("", response_model=list[SchoolRead])
def list_schools(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[School]:
    del current_user
    return db.query(School).all()
