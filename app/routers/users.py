from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from ..database import get_session
from ..models import User
from ..security import decode_jwt_and_groups

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
def current_user(
    payload=Depends(decode_jwt_and_groups),
    session: Session = Depends(get_session),
):
    user, groups = payload
    return {"id": user.id, "username": user.username, "email": user.email, "groups": groups}
