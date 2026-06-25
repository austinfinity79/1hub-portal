from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.fee import Fee


def create(db: Session, txn_id: str, merchant_id: str, fee_amount: int) -> Fee:
    """Create a fee record and flush (caller controls commit)."""
    fee = Fee(txn_id=txn_id, merchant_id=merchant_id, fee_amount=fee_amount)
    db.add(fee)
    db.flush()
    return fee


def list_fees(
    db: Session,
    status: str | None = None,
    merchant_id: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Fee], int]:
    """Return paginated fee records with optional filters.

    Returns:
        Tuple of (items, total_count).
    """
    query = db.query(Fee)

    if status is not None:
        query = query.filter(Fee.status == status)
    if merchant_id is not None:
        query = query.filter(Fee.merchant_id == merchant_id)

    total = query.count()

    items = (
        query.order_by(Fee.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return items, total


def sum_by_status(db: Session, status: str) -> int:
    """Return SUM(fee_amount) for fees matching the given status."""
    result = (
        db.query(func.sum(Fee.fee_amount))
        .filter(Fee.status == status)
        .scalar()
    )
    return result or 0
