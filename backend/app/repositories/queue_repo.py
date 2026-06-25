from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.notify_queue import NotifyQueue


def enqueue(db: Session, txn_id: str, merchant_id: str) -> NotifyQueue:
    """Add a notification to the queue and flush."""
    entry = NotifyQueue(txn_id=txn_id, merchant_id=merchant_id)
    db.add(entry)
    db.flush()
    return entry


def get_pending_by_merchant(db: Session, merchant_id: str) -> list[NotifyQueue]:
    """Return all queue entries for a merchant that have not been batched yet."""
    return (
        db.query(NotifyQueue)
        .filter(
            NotifyQueue.merchant_id == merchant_id,
            NotifyQueue.batched_at.is_(None),
        )
        .order_by(NotifyQueue.queued_at)
        .all()
    )


def count_pending(db: Session) -> int:
    """Return the total number of un-batched queue entries."""
    return (
        db.query(func.count(NotifyQueue.id))
        .filter(NotifyQueue.batched_at.is_(None))
        .scalar()
        or 0
    )


def mark_batched(db: Session, queue_ids: list[str]) -> None:
    """Set batched_at = utcnow for the given queue entry IDs."""
    if not queue_ids:
        return
    db.query(NotifyQueue).filter(NotifyQueue.id.in_(queue_ids)).update(
        {"batched_at": datetime.utcnow()}, synchronize_session="fetch"
    )
    db.flush()
