from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlmodel import Session
from sqlmodel import select

from ..database.models import Group, GroupMembership, User, datetime_now
from ..database.models import UserPasswordHash

from ..database import get_session
from ..security import create_access_token, hash_password, verify_password, decode_jwt_and_groups, get_current_user


router = APIRouter(tags=["General"])


@router.get("/health")
async def healthcheck():
    return {"status": "ok"}



@router.post("/register")
async def register(email: str, password: str, session: Session = Depends(get_session)):
    email = email.strip().lower()

    if session.exec(select(User).where(User.email == email)).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed = hash_password(password)
    user = User(email=email, password_hash=hashed)
    session.add(user)
    session.flush()
    session.add(UserPasswordHash(user_id=user.id, password_hash=hashed, created_at=datetime_now()))

    root_group = session.exec(
        select(Group).where(
            Group.name == "Admin",
            Group.scope_type == "root",
            Group.scope_id == 0,
        )
    ).first()

    if root_group is None:
        root_group = Group(name="Admin", scope_type="root", scope_id=0)
        session.add(root_group)
        session.flush()
        session.add(GroupMembership(group_id=root_group.id, user_id=user.id))

    session.commit()
    token, expires = create_access_token(user)
    return {"access_token": token, "token_type": "bearer", "expires": expires}


@router.post("/login")
async def login(email: str, password: str, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == email)).first()
    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token, expires = create_access_token(user)
    return {"access_token": token, "token_type": "bearer", "expires": expires}


@router.post("/reset-password")
async def reset_password(
        new_password: str,
        user: User = Depends(get_current_user),
        session: Session = Depends(get_session),
):
    hashed = hash_password(new_password)
    user.password_hash = hashed
    session.add(UserPasswordHash(user_id=user.id, password_hash=hashed, created_at=datetime_now()))
    session.add(user)
    session.commit()
    token, expires = create_access_token(user)
    return {"access_token": token, "token_type": "bearer", "expires": expires}
