from sqlalchemy import ForeignKey
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TeacherClass(Base):
    __tablename__ = "teacher_classes"

    teacher_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False), ForeignKey("teachers.id"), primary_key=True
    )
    class_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False), ForeignKey("classes.id"), primary_key=True
    )
