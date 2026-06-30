"""Authentication service: login, refresh, logout, user creation."""

import json
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.core.auth import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.models.audit_log import AuditLog
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.auth import TokenResponse, UserCreate, UserOut


def login(db: Session, username: str, password: str, ip: str | None = None) -> TokenResponse:
    """Authenticate user and return access + refresh tokens."""
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    access_token = create_access_token({"sub": user.id, "role": user.role})
    raw_refresh = create_refresh_token()

    refresh = RefreshToken(
        id=str(uuid4()),
        user_id=user.id,
        token_hash=hash_token(raw_refresh),
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(refresh)

    db.add(AuditLog(
        id=str(uuid4()),
        user_id=user.id,
        action="LOGIN",
        resource_type="user",
        resource_id=user.id,
        ip_address=ip,
    ))
    db.commit()

    return TokenResponse(access_token=access_token, refresh_token=raw_refresh)


def refresh(db: Session, raw_refresh_token: str) -> TokenResponse:
    """Exchange a valid refresh token for a new token pair."""
    token_h = hash_token(raw_refresh_token)
    stored = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token_hash == token_h,
            RefreshToken.revoked == False,  # noqa: E712
        )
        .first()
    )
    if not stored:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    # SQLite stores naive UTC datetimes, so compare consistently
    if stored.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )

    user = db.query(User).filter(User.id == stored.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or deactivated",
        )

    # Revoke old token
    stored.revoked = True

    # Issue new pair
    access_token = create_access_token({"sub": user.id, "role": user.role})
    new_raw_refresh = create_refresh_token()

    new_refresh = RefreshToken(
        id=str(uuid4()),
        user_id=user.id,
        token_hash=hash_token(new_raw_refresh),
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(new_refresh)
    db.commit()

    return TokenResponse(access_token=access_token, refresh_token=new_raw_refresh)


def logout(db: Session, raw_refresh_token: str) -> None:
    """Revoke a refresh token."""
    token_h = hash_token(raw_refresh_token)
    stored = (
        db.query(RefreshToken)
        .filter(RefreshToken.token_hash == token_h)
        .first()
    )
    if stored:
        stored.revoked = True
        db.commit()


def create_user(
    db: Session, data: UserCreate, created_by_user: User
) -> UserOut:
    """Create a new portal user (admin only)."""
    if created_by_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create users",
        )

    # Check duplicates
    existing = (
        db.query(User)
        .filter((User.username == data.username) | (User.email == data.email))
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists",
        )

    user = User(
        id=str(uuid4()),
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
        role=data.role,
        is_active=True,
    )
    db.add(user)

    db.add(AuditLog(
        id=str(uuid4()),
        user_id=created_by_user.id,
        action="USER_CREATED",
        resource_type="user",
        resource_id=user.id,
        detail=json.dumps({"username": user.username, "role": user.role}),
    ))
    db.commit()
    db.refresh(user)

    return UserOut.model_validate(user)
