from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.database import Base


class RegistrationRequest(Base):

    __tablename__ = "registration_requests"

    request_id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    school_id = Column(
        Integer,
        ForeignKey("schools.school_id"),
        nullable=False
    )

    parent_email = Column(String(255))

    profile_data = Column(JSONB)

    created_at = Column(
        DateTime,
        server_default=func.current_timestamp()
    )

    reviewed_by = Column(
        Integer,
        ForeignKey("users.user_id")
    )

    reviewed_at = Column(DateTime)

    rejection_reason = Column(Text)