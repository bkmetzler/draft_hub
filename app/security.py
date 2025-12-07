import hashlib
import hmac
import os
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Any

import jwt

from app.settings import get_settings

settings = get_settings()


def _pbkdf2_hash(password: str, salt: bytes) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 390000)
    return dk.hex()


def hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or os.urandom(16)
    hashed = _pbkdf2_hash(password, salt)
    return f"{salt.hex()}:{hashed}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, hashed = stored.split(":", 1)
    except ValueError:
        return False
    salt = bytes.fromhex(salt_hex)
    candidate = _pbkdf2_hash(password, salt)
    return hmac.compare_digest(candidate, hashed)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode: dict[str, Any] = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
