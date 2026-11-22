from datetime import datetime, timedelta, timezone
from hashlib import sha256
from uuid import uuid4
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from backend.app.core.config import get_settings
from backend.app.db.session import get_db
from backend.app.models.tables import User
from backend.app.security.passwords import verify_password
from backend.app.security.dependencies import bearer, current_user
from fastapi.security import HTTPAuthorizationCredentials

router = APIRouter(prefix='/auth', tags=['authentication'])

class LoginInput(BaseModel):
    email: EmailStr
    password: str

class UserOutput(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    email: str
    role: str

    model_config = {'from_attributes': True}

class LoginOutput(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    expires_in_seconds: int
    user: UserOutput

@router.post('/login', response_model=LoginOutput)
def login(payload: LoginInput, db: Session = Depends(get_db)):
    # Normalize addresses on read; demo seed uses lower-case email addresses.
    email = str(payload.email).strip().lower()
    user = db.scalar(select(User).where(User.email == email))
    if user is None or not user.is_active or not verify_password(payload.password, user.password_hash):
        db.execute(text("INSERT INTO public.auth_audit_log(user_id,email_attempt,event) VALUES(:uid,:email,'login_failed')"), {'uid': user.user_id if user else None, 'email': email})
        db.commit()
        raise HTTPException(status_code=401, detail='Invalid email or password')
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=settings.access_token_minutes)
    jti = str(uuid4())
    token = jwt.encode({'sub': str(user.user_id), 'jti': jti, 'iat': now, 'exp': expires, 'iss': settings.jwt_issuer}, settings.jwt_secret, algorithm='HS256')
    db.execute(text('INSERT INTO public.auth_sessions(id,user_id,token_sha256,expires_at) VALUES(CAST(:id AS uuid),:uid,:hash,:expires)'), {'id': jti, 'uid': user.user_id, 'hash': sha256(token.encode()).hexdigest(), 'expires': expires})
    db.execute(text("INSERT INTO public.auth_audit_log(user_id,event) VALUES(:uid,'login_success')"), {'uid': user.user_id})
    db.commit()
    return LoginOutput(access_token=token, expires_in_seconds=settings.access_token_minutes*60, user=UserOutput.model_validate(user))

@router.get('/me', response_model=UserOutput)
def me(user: User = Depends(current_user)):
    return user

@router.post('/logout', status_code=204)
def logout(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), user: User = Depends(current_user), db: Session = Depends(get_db)):
    digest = sha256(credentials.credentials.encode()).hexdigest()
    db.execute(text('UPDATE public.auth_sessions SET revoked_at=now() WHERE user_id=:uid AND token_sha256=:digest'), {'uid': user.user_id, 'digest': digest})
    db.execute(text("INSERT INTO public.auth_audit_log(user_id,event) VALUES(:uid,'logout')"), {'uid': user.user_id})
    db.commit()
