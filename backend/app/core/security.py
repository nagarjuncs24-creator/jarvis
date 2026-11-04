from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from jwt import InvalidTokenError
from pwdlib import PasswordHash

from app.core.config import get_settings

password_hash = PasswordHash.recommended()
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def create_token(subject: UUID, token_type: str, expires_delta: timedelta) -> str:
    expires_at = datetime.now(UTC) + expires_delta
    return jwt.encode(
        {"sub": str(subject), "type": token_type, "exp": expires_at},
        get_settings().app_secret_key,
        algorithm=ALGORITHM,
    )


def create_access_token(subject: UUID) -> str:
    return create_token(subject, "access", timedelta(minutes=get_settings().access_token_expire_minutes))


def create_refresh_token(subject: UUID) -> str:
    return create_token(subject, "refresh", timedelta(days=get_settings().refresh_token_expire_days))


def decode_token(token: str, expected_type: str) -> UUID:
    try:
        payload = jwt.decode(token, get_settings().app_secret_key, algorithms=[ALGORITHM])
        if payload.get("type") != expected_type:
            raise ValueError("Unexpected token type")
        return UUID(payload["sub"])
    except (InvalidTokenError, KeyError, ValueError) as error:
        raise ValueError("Invalid or expired token") from error
