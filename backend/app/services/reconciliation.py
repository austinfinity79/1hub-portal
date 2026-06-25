from datetime import date

from sqlalchemy import cast, Date, func
from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.napas.client import NapasClient
from app.repositories import reconciliation_repo
from app.services.txn_state import transition


def run_reconciliation(
    db: Session, napas_client: NapasClient, recon_date: date
) -> dict:
    """Doi soat cuoi ngay: so khop giao dich 1Hub voi bao cao Napas.

    - KHOP: so tien khop giua ledger va Napas
    - LECH: sai lech hoac thieu trong bao cao Napas
    """
    # 1. Lay bao cao thanh toan tu Napas
    napas_records = napas_client.get_settlement_report(recon_date)
    napas_map: dict[str, int] = {r.full_order_id: r.amount for r in napas_records}

    # 2. Lay giao dich da ACSC trong ngay tu DB
    ledger_txns: list[Transaction] = (
        db.query(Transaction)
        .filter(
            Transaction.state.in_(["SETTLED", "NOTIFIED", "QUEUED"]),
            cast(Transaction.notice_acsc_at, Date) == recon_date,
        )
        .all()
    )

    count_khop = 0
    count_lech = 0

    # 3. Doi soat tung giao dich
    for txn in ledger_txns:
        napas_amount = napas_map.get(txn.full_order_id)

        if napas_amount is not None and napas_amount == txn.amount:
            # Khop
            reconciliation_repo.create(
                db, recon_date, txn.id, txn.amount, napas_amount, "KHOP"
            )
            if txn.state in ("NOTIFIED", "SETTLED"):
                transition(db, txn, "RECONCILED")
            count_khop += 1
        else:
            # Lech hoac thieu trong bao cao Napas
            reconciliation_repo.create(
                db,
                recon_date,
                txn.id,
                txn.amount,
                napas_amount if napas_amount is not None else 0,
                "LECH",
            )
            if txn.state in ("NOTIFIED", "SETTLED"):
                transition(db, txn, "DISPUTE")
            count_lech += 1

    db.commit()

    return {
        "date": str(recon_date),
        "total": count_khop + count_lech,
        "matched": count_khop,
        "mismatched": count_lech,
    }
