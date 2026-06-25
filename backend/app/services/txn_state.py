from sqlalchemy.orm import Session

from app.core.exceptions import InvalidStateTransition
from app.models.transaction import Transaction
from app.repositories import transaction_repo

# Bang chuyen trang thai hop le
VALID_TRANSITIONS: dict[str, set[str]] = {
    "INITIATED": {"AUTHORIZED", "REJECTED"},
    "AUTHORIZED": {"SETTLED", "REJECTED"},
    "SETTLED": {"NOTIFIED", "QUEUED", "RECONCILED", "DISPUTE"},
    "QUEUED": {"NOTIFIED"},
    "NOTIFIED": {"RECONCILED", "DISPUTE"},
}


def validate_transition(current_state: str, next_state: str) -> bool:
    """Kiem tra chuyen trang thai co hop le khong."""
    allowed = VALID_TRANSITIONS.get(current_state, set())
    return next_state in allowed


def transition(
    db: Session, txn: Transaction, next_state: str, **extra_fields: object
) -> Transaction:
    """Chuyen trang thai giao dich, raise loi neu khong hop le."""
    if not validate_transition(txn.state, next_state):
        raise InvalidStateTransition(txn.state, next_state)
    return transaction_repo.update_state(db, txn, next_state, **extra_fields)
