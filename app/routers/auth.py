from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database.models import User, UserPasswordHash, datetime_now
from ..database import get_session
from ..security import create_access_token, hash_password, verify_password, decode_jwt_and_groups, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

