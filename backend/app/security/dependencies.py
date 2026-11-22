from datetime import datetime, timezone
from hashlib import sha256
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.app.core.config import get_settings
from backend.app.db.session import get_db
from backend.app.models.tables import User

bearer = HTTPBearer(auto_error=False)

def unauthorized():
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid or expired session', headers={'WWW-Authenticate': 'Bearer'})

def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> User:
    if not credentials or credentials.scheme.lower() != 'bearer':
        unauthorized()
    settings = get_settings()
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=['HS256'], issuer=settings.jwt_issuer, options={'require': ['sub','jti','exp','iss']})
        user_id = int(payload['sub'])
        jti = payload['jti']
    except (jwt.InvalidTokenError, ValueError, KeyError, TypeError):
        unauthorized()
    row = db.execute(text('SELECT user_id FROM public.auth_sessions WHERE id=CAST(:jti AS uuid) AND token_sha256=:digest AND revoked_at IS NULL AND expires_at>now()'), {'jti': jti, 'digest': sha256(token.encode()).hexdigest()}).first()
    if row is None or row.user_id != user_id:
        unauthorized()
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        unauthorized()
    return user

def roles_allowed(*roles: str):
    def role_check(user: User = Depends(current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(403, detail='Not authorized for this role')
        return user
    return role_check
