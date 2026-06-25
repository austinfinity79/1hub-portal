"""Merchant listing and detail routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import merchant_repo
from app.schemas.merchant import MerchantOut

router = APIRouter(prefix="/api/merchants", tags=["Merchants"])


@router.get("", response_model=list[MerchantOut])
def list_merchants(
    db: Session = Depends(get_db),
) -> list[MerchantOut]:
    """List all merchants."""
    merchants = merchant_repo.get_all(db)
    return [MerchantOut.model_validate(m) for m in merchants]


@router.get("/{merchant_id}", response_model=MerchantOut)
def get_merchant(
    merchant_id: str,
    db: Session = Depends(get_db),
) -> MerchantOut:
    """Get a single merchant by ID."""
    m = merchant_repo.get_by_id(db, merchant_id)
    if not m:
        raise HTTPException(status_code=404, detail="Merchant not found")
    return MerchantOut.model_validate(m)
