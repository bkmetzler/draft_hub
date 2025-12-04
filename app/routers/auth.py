from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database.models import User, UserPasswordHash, datetime_now
from ..database import get_session
from ..security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(email: str, password: str, session: Session = Depends(get_session)):
    email = email.strip().lower()

    if session.exec(select(User).where(User.email == email)).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed = hash_password(password)
    user = User(email=email, password_hash=hashed)
    session.add(user)
    session.flush()
    session.add(UserPasswordHash(user_id=user.id, password_hash=hashed, created_at=datetime_now()))
    session.commit()
    token, expires = create_access_token(user)
    return {"access_token": token, "token_type": "bearer", "expires": expires}


@router.post("/login")
def login(username: str, password: str, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token, expires = create_access_token(user)
    return {"access_token": token, "token_type": "bearer", "expires": expires}


@router.post("/reset-password")
def reset_password(
        username: str,
        new_password: str,
        session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    hashed = hash_password(new_password)
    user.password_hash = hashed
    session.add(UserPasswordHash(user_id=user.id, password_hash=hashed, created_at=datetime_now()))
    session.add(user)
    session.commit()
    token, expires = create_access_token(user)
    return {"access_token": token, "token_type": "bearer", "expires": expires}
