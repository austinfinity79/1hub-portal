from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.transaction import Transaction


def get_by_id(db: Session, txn_id: str) -> Transaction | None:
    """Return a transaction by primary key."""
    return db.query(Transaction).filter(Transaction.id == txn_id).first()


def get_by_order_id(db: Session, full_order_id: str) -> Transaction | None:
    """Return a transaction by its unique full_order_id."""
    return (
        db.query(Transaction)
        .filter(Transaction.full_order_id == full_order_id)
        .first()
    )


def create(db: Session, **kwargs: object) -> Transaction:
    """Create a new transaction and flush (caller controls commit)."""
    txn = Transaction(**kwargs)
    db.add(txn)
    db.flush()
    return txn


def update_state(
    db: Session, txn: Transaction, new_state: str, **extra_fields: object
) -> Transaction:
    """Update transaction state and any extra fields, then flush."""
    txn.state = new_state
    for field, value in extra_fields.items():
        setattr(txn, field, value)
    db.flush()
    return txn


def _parse_date(date_str: str) -> datetime:
    """Parse a dd/mm/yyyy string into a datetime."""
    return datetime.strptime(date_str, "%d/%m/%Y")


def list_transactions(
    db: Session,
    merchant_id: str | None = None,
    state: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Transaction], int]:
    """Return paginated transactions with optional filters.

    Args:
        db: Database session.
        merchant_id: Filter by merchant.
        state: Filter by transaction state.
        date_from: Start date inclusive (dd/mm/yyyy).
        date_to: End date inclusive (dd/mm/yyyy), covers the entire day.
        page: 1-based page number.
        page_size: Items per page.

    Returns:
        Tuple of (items, total_count).
    """
    query = db.query(Transaction)

    if merchant_id is not None:
        query = query.filter(Transaction.merchant_id == merchant_id)
    if state is not None:
        query = query.filter(Transaction.state == state)
    if date_from is not None:
        dt_from = _parse_date(date_from)
        query = query.filter(Transaction.created_at >= dt_from)
    if date_to is not None:
        # End of the given day (next day at 00:00)
        dt_to = _parse_date(date_to).replace(hour=23, minute=59, second=59)
        query = query.filter(Transaction.created_at <= dt_to)

    total = query.count()

    items = (
        query.order_by(Transaction.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return items, total
