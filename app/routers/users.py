from fastapi import APIRouter
from fastapi import Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.database.models import User
from app.database.models import UserRead

router = APIRouter(prefix="/api/v1/user", tags=["user"])


@router.get("", response_model=list[UserRead])
async def list_users(session: AsyncSession = Depends(get_session)) -> list[UserRead]:
    result = await session.exec(select(User))
    users = result.all()
    return [UserRead(id=user.id, username=user.username, email=user.email) for user in users]
