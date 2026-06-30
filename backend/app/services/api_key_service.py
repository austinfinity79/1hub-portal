"""Merchant API Key management service."""

import json
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import (
    decrypt_api_key,
    encrypt_api_key,
    generate_api_key,
    hash_api_key,
    verify_password,
)
from app.models.audit_log import AuditLog
from app.models.merchant import Merchant
from app.models.merchant_api_key import MerchantApiKey
from app.models.user import User
from app.schemas.merchant_api_key import ApiKeyCreatedOut, ApiKeyOut


def create_key(
    db: Session,
    merchant_id: str,
    label: str,
    created_by_user: User,
    ip: str | None = None,
) -> ApiKeyCreatedOut:
    """Generate and store a new API key for a merchant."""
    # Verify merchant exists
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant not found",
        )

    raw_key = generate_api_key()
    key_h = hash_api_key(raw_key)
    ciphertext, nonce = encrypt_api_key(raw_key)

    api_key = MerchantApiKey(
        id=str(uuid4()),
        merchant_id=merchant_id,
        label=label,
        key_prefix=raw_key[:8],
        key_hash=key_h,
        key_ciphertext=ciphertext,
        key_nonce=nonce,
        is_active=True,
        created_by=created_by_user.id,
    )
    db.add(api_key)

    db.add(AuditLog(
        id=str(uuid4()),
        user_id=created_by_user.id,
        action="KEY_CREATED",
        resource_type="merchant_api_key",
        resource_id=api_key.id,
        detail=json.dumps({"merchant_id": merchant_id, "label": label}),
        ip_address=ip,
    ))
    db.commit()
    db.refresh(api_key)

    out = ApiKeyOut.model_validate(api_key)
    return ApiKeyCreatedOut(**out.model_dump(), full_key=raw_key)


def list_keys(db: Session, merchant_id: str) -> list[ApiKeyOut]:
    """List all API keys for a merchant."""
    keys = (
        db.query(MerchantApiKey)
        .filter(MerchantApiKey.merchant_id == merchant_id)
        .order_by(MerchantApiKey.created_at.desc())
        .all()
    )
    return [ApiKeyOut.model_validate(k) for k in keys]


def revoke_key(
    db: Session,
    key_id: str,
    user: User,
    ip: str | None = None,
) -> None:
    """Revoke (deactivate) an API key."""
    api_key = db.query(MerchantApiKey).filter(MerchantApiKey.id == key_id).first()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    api_key.is_active = False

    db.add(AuditLog(
        id=str(uuid4()),
        user_id=user.id,
        action="KEY_REVOKED",
        resource_type="merchant_api_key",
        resource_id=key_id,
        detail=json.dumps({"merchant_id": api_key.merchant_id, "label": api_key.label}),
        ip_address=ip,
    ))
    db.commit()


def reveal_key(
    db: Session,
    key_id: str,
    password: str,
    user: User,
    ip: str | None = None,
) -> str:
    """Decrypt and return an API key. Requires user password re-verification."""
    # Re-verify caller's password
    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
        )

    api_key = db.query(MerchantApiKey).filter(MerchantApiKey.id == key_id).first()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    plaintext = decrypt_api_key(api_key.key_ciphertext, api_key.key_nonce)

    db.add(AuditLog(
        id=str(uuid4()),
        user_id=user.id,
        action="KEY_REVEALED",
        resource_type="merchant_api_key",
        resource_id=key_id,
        detail=json.dumps({"merchant_id": api_key.merchant_id}),
        ip_address=ip,
    ))
    db.commit()

    return plaintext
