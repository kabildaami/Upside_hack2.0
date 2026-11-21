from typing import Literal
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):

    first_name: str = Field(min_length=2, max_length=100)
    last_name: str = Field(min_length=2, max_length=100)

    email: EmailStr
    password: str = Field(min_length=8)

    phone: str | None = None

    role: Literal["parent", "student", "teacher"]

    school_id: int

    parent_email: EmailStr | None = None

    profile_data: dict = Field(default_factory=dict)