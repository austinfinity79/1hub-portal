"""User management routes (admin only)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.database import get_db
from app.models.user import User
from app.schemas.auth import UserCreate, UserOut
from app.services import auth_service

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> list[UserOut]:
    """List all portal users (admin only)."""
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [UserOut.model_validate(u) for u in users]


@router.post("", response_model=UserOut, status_code=201)
def create_user(
    body: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> UserOut:
    """Create a new portal user (admin only)."""
    return auth_service.create_user(db, body, current_user)
