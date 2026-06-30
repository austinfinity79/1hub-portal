"""Authentication routes: login, refresh, logout, me."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse, UserOut
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    body: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Authenticate and receive JWT tokens."""
    ip = request.client.host if request.client else None
    return auth_service.login(db, body.username, body.password, ip=ip)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    body: RefreshRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Exchange a refresh token for a new token pair."""
    return auth_service.refresh(db, body.refresh_token)


@router.post("/logout")
def logout(
    body: RefreshRequest,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Revoke a refresh token."""
    auth_service.logout(db, body.refresh_token)
    return {"detail": "Logged out"}


@router.get("/me", response_model=UserOut)
def get_me(
    current_user: User = Depends(get_current_user),
) -> UserOut:
    """Return the currently authenticated user."""
    return UserOut.model_validate(current_user)
