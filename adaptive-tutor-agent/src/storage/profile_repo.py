import json
import os
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import Column, JSON, String, create_engine
from sqlalchemy.orm import declarative_base, Session, sessionmaker

from src.models.student_profile import StudentProfile


Base = declarative_base()


class ProfileRow(Base):
    __tablename__ = "student_profiles"
    student_id = Column(String, primary_key=True)
    encrypted_profile = Column(String, nullable=False)


def _fernet() -> Fernet:
    key = os.getenv("PROFILE_ENCRYPTION_KEY")
    if not key:
        key = "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA="
    try:
        return Fernet(key.encode())
    except Exception:
        import base64
        import hashlib
        derived = base64.urlsafe_b64encode(hashlib.sha256(key.encode()).digest())
        return Fernet(derived)


class ProfileRepo:
    def __init__(self, database_url: str = "sqlite:///./adaptive_tutor.db"):
        connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
        self.engine = create_engine(database_url, connect_args=connect_args)
        Base.metadata.create_all(self.engine)
        self.session_factory = sessionmaker(bind=self.engine)
        self.fernet = _fernet()

    def get(self, student_id: str) -> StudentProfile:
        with self.session_factory() as db:
            row = db.get(ProfileRow, student_id)
            if not row:
                profile = StudentProfile(student_id=student_id)
                self.upsert(profile)
                return profile
            try:
                data = json.loads(self.fernet.decrypt(row.encrypted_profile.encode()).decode())
            except InvalidToken:
                raise RuntimeError("Encrypted student profile could not be decrypted")
            return StudentProfile.model_validate(data)

    def upsert(self, profile: StudentProfile) -> StudentProfile:
        encrypted = self.fernet.encrypt(profile.model_dump_json().encode()).decode()
        with self.session_factory() as db:
            row = db.get(ProfileRow, profile.student_id)
            if row:
                row.encrypted_profile = encrypted
            else:
                db.add(ProfileRow(student_id=profile.student_id, encrypted_profile=encrypted))
            db.commit()
        return profile
