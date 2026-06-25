from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.reconciliation import Reconciliation


def create(
    db: Session,
    recon_date: date,
    txn_id: str,
    ledger_amount: int,
    napas_amount: int,
    result: str,
) -> Reconciliation:
    """Create a reconciliation record and flush."""
    rec = Reconciliation(
        recon_date=recon_date,
        txn_id=txn_id,
        ledger_amount=ledger_amount,
        napas_amount=napas_amount,
        result=result,
    )
    db.add(rec)
    db.flush()
    return rec


def list_by_date(db: Session, recon_date: date) -> list[Reconciliation]:
    """Return all reconciliation records for a given date."""
    return (
        db.query(Reconciliation)
        .filter(Reconciliation.recon_date == recon_date)
        .order_by(Reconciliation.created_at)
        .all()
    )


def count_disputes(db: Session) -> int:
    """Return the number of reconciliation records with result LECH."""
    return (
        db.query(func.count(Reconciliation.id))
        .filter(Reconciliation.result == "LECH")
        .scalar()
        or 0
    )
