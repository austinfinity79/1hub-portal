"""Merchant API Key management routes."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.database import get_db
from app.models.user import User
from app.schemas.merchant_api_key import (
    ApiKeyCreate,
    ApiKeyCreatedOut,
    ApiKeyOut,
    ApiKeyRevealRequest,
    ApiKeyRevealResponse,
)
from app.services import api_key_service

router = APIRouter(prefix="/api/merchant-keys", tags=["API Keys"])


@router.get("/{merchant_id}", response_model=list[ApiKeyOut])
def list_keys(
    merchant_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> list[ApiKeyOut]:
    """List all API keys for a merchant (admin only)."""
    return api_key_service.list_keys(db, merchant_id)


@router.post("", response_model=ApiKeyCreatedOut, status_code=201)
def create_key(
    body: ApiKeyCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> ApiKeyCreatedOut:
    """Create a new API key for a merchant (admin only).

    The full key is returned ONLY in this response.
    """
    ip = request.client.host if request.client else None
    return api_key_service.create_key(
        db, body.merchant_id, body.label, current_user, ip=ip
    )


@router.delete("/{key_id}", status_code=204)
def revoke_key(
    key_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> None:
    """Revoke an API key (admin only)."""
    ip = request.client.host if request.client else None
    api_key_service.revoke_key(db, key_id, current_user, ip=ip)


@router.post("/{key_id}/reveal", response_model=ApiKeyRevealResponse)
def reveal_key(
    key_id: str,
    body: ApiKeyRevealRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> ApiKeyRevealResponse:
    """Decrypt and reveal an API key (admin only, requires password)."""
    ip = request.client.host if request.client else None
    key = api_key_service.reveal_key(
        db, key_id, body.password, current_user, ip=ip
    )
    return ApiKeyRevealResponse(key=key)
