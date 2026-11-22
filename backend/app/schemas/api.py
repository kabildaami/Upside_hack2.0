from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator
from typing import Literal

class LabelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    label: str

class SubjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    subject_id: int
    subject_name: str
    school_level: str

class StudentCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    # Never accept or return a raw password in this endpoint; auth is out of scope.
    password_hash: str = Field(min_length=1)
    parent_id: int
    school_id: int
    date_of_birth: date | None = None
    gender: str | None = None

class StudentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    student_id: int
    user_id: int
    parent_id: int
    school_id: int
    date_of_birth: date | None = None

class SurveyUpsert(BaseModel):
    school_level: Literal["primary", "high_school"]
    grade_level: Literal["1st primary", "2nd primary", "3rd primary", "4th primary", "5th primary", "6th primary", "7th grade", "8th grade", "9th grade", "10th grade", "11th grade", "12th grade"]
    field_of_study: str | None = None
    other_hobbies: str | None = None
    needs_details: str | None = None
    difficulty_level: int | None = Field(default=None, ge=1, le=5)
    help_wanted: str | None = None
    consent: Literal[True]
    hobby_ids: list[int] = Field(default_factory=list)
    need_ids: list[int] = Field(default_factory=list)
    problem_ids: list[int] = Field(default_factory=list)
    difficult_subject_ids: list[int] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_level(self):
        is_primary = self.grade_level.endswith("primary")
        if is_primary != (self.school_level == "primary"):
            raise ValueError("grade_level does not match school_level")
        return self

class SurveyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    student_id: int
    school_level: str
    grade_level: str
    difficulty_level: int | None
    consent: bool
    updated_at: datetime | None
