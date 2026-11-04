import hashlib
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.dependencies import CurrentUser, DatabaseSession
from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models import RefreshToken, User
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


def token_fingerprint(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def issue_tokens(database: DatabaseSession, user: User) -> TokenResponse:
    refresh_token = create_refresh_token(user.id)
    database.add(
        RefreshToken(
            user_id=user.id,
            token_hash=token_fingerprint(refresh_token),
            expires_at=datetime.now(UTC) + timedelta(days=get_settings().refresh_token_expire_days),
        )
    )
    database.commit()
    return TokenResponse(access_token=create_access_token(user.id), refresh_token=refresh_token, user=user)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, database: DatabaseSession) -> TokenResponse:
    email = str(payload.email).lower()
    if database.scalar(select(User.id).where(User.email == email)) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered")
    user = User(email=email, password_hash=hash_password(payload.password), display_name=payload.display_name)
    database.add(user)
    database.flush()
    return issue_tokens(database, user)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, database: DatabaseSession) -> TokenResponse:
    user = database.scalar(select(User).where(User.email == str(payload.email).lower()))
    if user is None or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return issue_tokens(database, user)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, database: DatabaseSession) -> TokenResponse:
    try:
        user_id = decode_token(payload.refresh_token, "refresh")
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from error
    stored = database.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_fingerprint(payload.refresh_token)))
    now = datetime.now(UTC)
    if stored is None or stored.user_id != user_id or stored.revoked_at is not None or stored.expires_at <= now:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    user = database.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    stored.revoked_at = now
    return issue_tokens(database, user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: RefreshRequest, database: DatabaseSession) -> None:
    stored = database.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_fingerprint(payload.refresh_token)))
    if stored is not None:
        stored.revoked_at = datetime.now(UTC)
        database.commit()


@router.get("/me", response_model=UserResponse)
def current_user(user: CurrentUser) -> User:
    return user
