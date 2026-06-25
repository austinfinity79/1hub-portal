from datetime import datetime

from sqlalchemy.orm import Session

from app.models.merchant import Merchant
from app.models.transaction import Transaction
from app.repositories import merchant_repo, queue_repo, transaction_repo
from app.services.txn_state import transition


def route_notification(db: Session, txn: Transaction, merchant: Merchant) -> None:
    """Dinh tuyen thong bao theo notify_mode cua merchant.

    - mode 1: gui realtime ngay lap tuc
    - mode 2: xep hang doi batch
    """
    if merchant.notify_mode == 1:
        _send_realtime(txn, merchant)
        transition(db, txn, "NOTIFIED", notified_at=datetime.utcnow())
    elif merchant.notify_mode == 2:
        queue_repo.enqueue(db, txn.id, merchant.id)
        transition(db, txn, "QUEUED")


def run_batch(db: Session) -> dict:
    """Gui batch thong bao cho tat ca merchant co notify_mode == 2.

    Gom cac queue entry chua gui, gui batch, danh dau da gui.
    """
    merchants = merchant_repo.get_all(db)
    merchants_processed = 0
    notifications_sent = 0

    for merchant in merchants:
        if merchant.notify_mode != 2:
            continue

        pending = queue_repo.get_pending_by_merchant(db, merchant.id)
        if not pending:
            continue

        # Gui batch (mock)
        print(
            f"[NOTIFY] Batch -> {merchant.name}: "
            f"{len(pending)} giao dich cho xu ly"
        )

        queue_ids = [entry.id for entry in pending]
        queue_repo.mark_batched(db, queue_ids)

        # Chuyen trang thai tung giao dich QUEUED -> NOTIFIED
        for entry in pending:
            txn = transaction_repo.get_by_id(db, entry.txn_id)
            if txn and txn.state == "QUEUED":
                transition(db, txn, "NOTIFIED", notified_at=datetime.utcnow())
                notifications_sent += 1

        merchants_processed += 1

    db.commit()
    return {"merchants_processed": merchants_processed, "notifications_sent": notifications_sent}


def _send_realtime(txn: Transaction, merchant: Merchant) -> None:
    """Mock gui thong bao realtime."""
    print(
        f"[NOTIFY] Realtime -> {merchant.name}: "
        f"Txn {txn.full_order_id} settled {txn.amount}d"
    )
