from datetime import date, datetime
from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, ForeignKey, ForeignKeyConstraint, Integer, SmallInteger, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.db.session import Base

class User(Base):
    __tablename__ = "users"
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(Text)
    phone: Mapped[str | None] = mapped_column(String(30))
    role: Mapped[str] = mapped_column(String(20))
    is_active: Mapped[bool | None] = mapped_column(Boolean, server_default="true")
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.current_timestamp())
    __table_args__ = (CheckConstraint("role IN ('student','parent','teacher','director','admin')"),)

class School(Base):
    __tablename__ = "schools"
    school_id: Mapped[int] = mapped_column(primary_key=True)
    school_name: Mapped[str] = mapped_column(String(200))
    address: Mapped[str | None] = mapped_column(Text)
    city: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(30))
    email: Mapped[str | None] = mapped_column(String(255))
    educational_level: Mapped[str | None] = mapped_column(String(100))
    director_user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), unique=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.current_timestamp())

class Parent(Base):
    __tablename__ = "parents"
    parent_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), unique=True)
    occupation: Mapped[str | None] = mapped_column(String(150))

class Director(Base):
    __tablename__ = "directors"
    director_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), unique=True)
    position: Mapped[str | None] = mapped_column(String(100), server_default="School Director")

class Teacher(Base):
    __tablename__ = "teachers"
    teacher_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), unique=True)
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.school_id"))
    specialization: Mapped[str | None] = mapped_column(String(150))
    hire_date: Mapped[date | None] = mapped_column(Date)
    __table_args__ = (UniqueConstraint("teacher_id", "school_id"),)

class Subject(Base):
    __tablename__ = "subjects"
    subject_id: Mapped[int] = mapped_column(primary_key=True)
    subject_name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    school_level: Mapped[str] = mapped_column(String(20))
    __table_args__ = (UniqueConstraint("subject_name", "school_level"), CheckConstraint("school_level IN ('primary', 'high_school')"))

class SchoolClass(Base):
    __tablename__ = "classes"
    class_id: Mapped[int] = mapped_column(primary_key=True)
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.school_id"))
    class_name: Mapped[str] = mapped_column(String(100))
    grade_level: Mapped[str | None] = mapped_column(String(50))
    academic_year: Mapped[str | None] = mapped_column(String(20))
    capacity: Mapped[int | None] = mapped_column(Integer)
    __table_args__ = (UniqueConstraint("class_id", "school_id"), UniqueConstraint("school_id", "class_name", "academic_year"), CheckConstraint("capacity > 0"))

class TeacherClass(Base):
    __tablename__ = "teacher_classes"
    assignment_id: Mapped[int] = mapped_column(primary_key=True)
    teacher_id: Mapped[int] = mapped_column(Integer)
    class_id: Mapped[int] = mapped_column(Integer)
    school_id: Mapped[int] = mapped_column(Integer)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.subject_id"))
    __table_args__ = (UniqueConstraint("teacher_id", "class_id", "subject_id"), ForeignKeyConstraint(["class_id", "school_id"], ["classes.class_id", "classes.school_id"]), ForeignKeyConstraint(["teacher_id", "school_id"], ["teachers.teacher_id", "teachers.school_id"]))

class Student(Base):
    __tablename__ = "students"
    student_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), unique=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("parents.parent_id"))
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.school_id"))
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    gender: Mapped[str | None] = mapped_column(String(30))
    address: Mapped[str | None] = mapped_column(Text)
    registration_date: Mapped[date | None] = mapped_column(Date, server_default=func.current_date())
    __table_args__ = (UniqueConstraint("student_id", "school_id"),)

class StudentSurvey(Base):
    __tablename__ = "student_survey"
    student_id: Mapped[int] = mapped_column(ForeignKey("students.student_id", ondelete="CASCADE"), primary_key=True)
    school_level: Mapped[str] = mapped_column(String(20))
    grade_level: Mapped[str] = mapped_column(String(40))
    field_of_study: Mapped[str | None] = mapped_column(String(120))
    other_hobbies: Mapped[str | None] = mapped_column(Text)
    needs_details: Mapped[str | None] = mapped_column(Text)
    difficulty_level: Mapped[int | None] = mapped_column(SmallInteger)
    help_wanted: Mapped[str | None] = mapped_column(Text)
    consent: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (CheckConstraint("school_level IN ('primary', 'high_school')"), CheckConstraint("grade_level IN ('1st primary','2nd primary','3rd primary','4th primary','5th primary','6th primary','7th grade','8th grade','9th grade','10th grade','11th grade','12th grade')"), CheckConstraint("difficulty_level BETWEEN 1 AND 5"), CheckConstraint("consent"))

class Hobby(Base):
    __tablename__ = "hobbies"
    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str] = mapped_column(String(80), unique=True)

class SpecialNeed(Base):
    __tablename__ = "special_needs"
    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str] = mapped_column(String(80), unique=True)

class StudyProblem(Base):
    __tablename__ = "study_problems"
    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str] = mapped_column(String(80), unique=True)

class StudentHobby(Base):
    __tablename__ = "student_hobbies"
    student_id: Mapped[int] = mapped_column(ForeignKey("students.student_id", ondelete="CASCADE"), primary_key=True)
    hobby_id: Mapped[int] = mapped_column(ForeignKey("hobbies.id", ondelete="CASCADE"), primary_key=True)

class StudentSpecialNeed(Base):
    __tablename__ = "student_special_needs"
    student_id: Mapped[int] = mapped_column(ForeignKey("students.student_id", ondelete="CASCADE"), primary_key=True)
    need_id: Mapped[int] = mapped_column(ForeignKey("special_needs.id", ondelete="CASCADE"), primary_key=True)

class StudentStudyProblem(Base):
    __tablename__ = "student_study_problems"
    student_id: Mapped[int] = mapped_column(ForeignKey("students.student_id", ondelete="CASCADE"), primary_key=True)
    problem_id: Mapped[int] = mapped_column(ForeignKey("study_problems.id", ondelete="CASCADE"), primary_key=True)

class StudentDifficultSubject(Base):
    __tablename__ = "student_difficult_subjects"
    student_id: Mapped[int] = mapped_column(ForeignKey("students.student_id", ondelete="CASCADE"), primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.subject_id", ondelete="CASCADE"), primary_key=True)
