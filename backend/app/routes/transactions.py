"""Transaction listing and detail routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import transaction_repo
from app.schemas.transaction import TransactionOut

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])


@router.get("")
def list_transactions(
    merchant_id: str | None = None,
    state: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
) -> dict:
    """List transactions with optional filters and pagination."""
    items, total = transaction_repo.list_transactions(
        db,
        merchant_id=merchant_id,
        state=state,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
    )
    return {
        "items": [TransactionOut.model_validate(t) for t in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{txn_id}", response_model=TransactionOut)
def get_transaction(
    txn_id: str,
    db: Session = Depends(get_db),
) -> TransactionOut:
    """Get a single transaction by ID."""
    txn = transaction_repo.get_by_id(db, txn_id)
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return TransactionOut.model_validate(txn)
