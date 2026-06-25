from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.repositories import fee_repo, queue_repo, reconciliation_repo

# Cac trang thai da xac nhan ACSC (da thanh toan qua Napas)
_SETTLED_STATES = {"SETTLED", "NOTIFIED", "QUEUED", "RECONCILED", "DISPUTE"}


def compute_metrics(db: Session) -> dict:
    """Tinh cac chi so KPI tong quan cho dashboard.

    - gmv_settled: tong gia tri giao dich da thanh toan (ACSC)
    - gmv_pending: tong gia tri giao dich dang cho (ACSP)
    - fee_receivable / fee_received: phi phai thu / da nhan
    - queue_pending: so thong bao cho gui batch
    - dispute_count: so ban ghi doi soat lech
    """
    gmv_settled = (
        db.query(func.sum(Transaction.amount))
        .filter(Transaction.state.in_(_SETTLED_STATES))
        .scalar()
    ) or 0

    gmv_pending = (
        db.query(func.sum(Transaction.amount))
        .filter(Transaction.state == "AUTHORIZED")
        .scalar()
    ) or 0

    return {
        "gmv_settled": gmv_settled,
        "gmv_pending": gmv_pending,
        "fee_receivable": fee_repo.sum_by_status(db, "PHAI_THU"),
        "fee_received": fee_repo.sum_by_status(db, "DA_NHAN"),
        "queue_pending": queue_repo.count_pending(db),
        "dispute_count": reconciliation_repo.count_disputes(db),
    }
