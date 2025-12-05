from fastapi import APIRouter, FastAPI
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlmodel import Session
from sqlmodel import select

from ..database.models import User
from ..database.models import UserPasswordHash

from ..database import get_session
from ..security import create_access_token, hash_password, verify_password, decode_jwt_and_groups, get_current_user
from fastapi.middleware.cors import CORSMiddleware


def configure_middleware(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
