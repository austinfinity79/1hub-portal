"""Fee listing routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import fee_repo
from app.schemas.fee import FeeOut

router = APIRouter(prefix="/api/fees", tags=["Fees"])


@router.get("")
def list_fees(
    status: str | None = None,
    merchant_id: str | None = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
) -> dict:
    """List fee records with optional filters and pagination."""
    items, total = fee_repo.list_fees(
        db,
        status=status,
        merchant_id=merchant_id,
        page=page,
        page_size=page_size,
    )
    return {
        "items": [FeeOut.model_validate(f) for f in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }
