from datetime import timedelta

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.database.models import User
from app.database.models import UserCreate
from app.database.models import UserPasswordHash
from app.security import create_access_token
from app.security import hash_password
from app.security import verify_password

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


@router.post("/register", response_model=UserCreate)
async def register_user(user: UserCreate, session: AsyncSession = Depends(get_session)) -> UserCreate:
    existing = await session.exec(select(User).where(User.username == user.username))
    if existing.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    hashed = hash_password(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    session.add(UserPasswordHash(user_id=db_user.id, hashed_password=hashed))
    await session.commit()
    return user


@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)
) -> dict[str, str]:
    result = await session.exec(select(User).where(User.username == form_data.username))
    user = result.first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=30)
    token = create_access_token(subject=str(user.id), expires_delta=access_token_expires)
    return {"access_token": token, "token_type": "bearer"}
