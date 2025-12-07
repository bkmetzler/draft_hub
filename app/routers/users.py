from __future__ import annotations

from typing import Sequence, Union

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ..database import get_session
from ..database.models import User
from ..security import decode_jwt_and_groups, get_current_user

router = APIRouter(prefix="/user", tags=["Users"], dependencies=[Depends(get_session)])


@router.get("/whoami")
async def get_who_am_i(
    payload=Depends(decode_jwt_and_groups),
) -> dict[str, Union[str, list[str]]]:
    user, groups = payload
    return {"id": user.id, "email": user.email, "groups": groups}


@router.get("/me")
def current_user(
    user: User = Depends(get_current_user),
):
    return {"id": user.id, "email": user.email, "groups": user.groups}


@router.get("/")
async def list_users(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Sequence[User]:
    stmt = select(User)
    return session.exec(stmt).all()
