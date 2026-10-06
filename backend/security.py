"""Password and access-token utilities for student accounts."""

from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash

from backend.config import settings
from backend.database import get_user_account

password_hasher = PasswordHash.recommended()
bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return password_hasher.verify(password, password_hash)


def create_access_token(user_id: int) -> str:
    if not settings.jwt_secret_key:
        raise RuntimeError("JWT_SECRET_KEY must be configured before issuing access tokens.")
    expires_at = datetime.now(timezone.utc) + timedelta(hours=12)
    return jwt.encode(
        {"sub": str(user_id), "exp": expires_at},
        settings.jwt_secret_key,
        algorithm="HS256",
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    if credentials is None or not settings.jwt_secret_key:
        raise HTTPException(status_code=401, detail="Authentication required.")
    try:
        claims = jwt.decode(credentials.credentials, settings.jwt_secret_key, algorithms=["HS256"])
        user_id = int(claims["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired access token.") from exc

    account = get_user_account(user_id)
    if account is None:
        raise HTTPException(status_code=401, detail="Account is no longer available.")
    return account


def get_current_student_id(user: dict = Depends(get_current_user)) -> int:
    return user["student_id"]
