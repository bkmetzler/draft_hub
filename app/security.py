from datetime import datetime, timedelta, timezone
from typing import List

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select
from werkzeug.security import check_password_hash, generate_password_hash

from app.database.models import GroupMembership, User

from .database import get_session
from .settings import get_settings

bearer_scheme = HTTPBearer(auto_error=False)
settings = get_settings()


def hash_password(raw_password: str) -> str:
    return generate_password_hash(raw_password)


def verify_password(raw_password: str, hashed: str) -> bool:
    return check_password_hash(hashed, raw_password)


def create_access_token(user: User) -> tuple[str, datetime]:
    expiration = datetime.now(tz=timezone.utc) + timedelta(minutes=settings.jwt_expiration_minutes)
    payload = {"sub": user.id, "email": user.email, "exp": expiration}
    token = jwt.encode(payload, settings.secret_key, algorithm="HS256")  # type: ignore[attr-defined]
    return token, expiration


def decode_jwt(token: str) -> dict:
    try:
        return jwt.decode(
            token, settings.secret_key, algorithms=["HS256"], options={"require": ["exp", "sub"]}
        )  # type: ignore[attr-defined]
    except jwt.exceptions.JWTException as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


def decode_jwt_and_groups(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: Session = Depends(get_session),
) -> tuple[User, List[str]]:
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    payload = decode_jwt(credentials.credentials)
    user = session.get(User, payload.get("sub"))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    group_names = [
        membership.group.name
        for membership in session.exec(
            select(GroupMembership).where(GroupMembership.user_id == user.id).options()
        ).all()
    ]
    return user, group_names


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: Session = Depends(get_session),
) -> User:
    user, _ = decode_jwt_and_groups(credentials, session)  # type: ignore[arg-type]
    return user
