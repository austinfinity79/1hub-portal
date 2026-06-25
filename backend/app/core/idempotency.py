from sqlalchemy.orm import Session

from app.models.transaction import Transaction


def is_notice_processed(db: Session, full_order_id: str, expected_status: str) -> bool:
    """
    Kiem tra notice da xu ly chua dua tren full_order_id + trang thai.

    - ACSP: neu txn da o AUTHORIZED hoac sau -> da xu ly
    - ACSC: neu txn da o SETTLED hoac sau -> da xu ly
    - RJCT: neu txn da o REJECTED -> da xu ly
    """
    txn = db.query(Transaction).filter(Transaction.full_order_id == full_order_id).first()
    if not txn:
        return False

    state_order: dict[str, int] = {
        "INITIATED": 0,
        "AUTHORIZED": 1,
        "SETTLED": 2,
        "QUEUED": 3,
        "NOTIFIED": 4,
        "RECONCILED": 5,
        "DISPUTE": 5,
        "REJECTED": -1,
    }

    if expected_status == "RJCT":
        return txn.state == "REJECTED"

    target_states: dict[str, str] = {"ACSP": "AUTHORIZED", "ACSC": "SETTLED"}
    target = target_states.get(expected_status)
    if not target:
        return False

    current_order = state_order.get(txn.state, -99)
    target_order = state_order.get(target, 0)
    return current_order >= target_order
