# TODO[NAPAS]: File này sẽ không dùng khi có Napas thật. Xem real.py
from datetime import date, datetime, timedelta

from app.database import SessionLocal
from app.models.transaction import Transaction
from app.napas.client import NapasClient, SettlementRecord, TxnStatusDTO


class MockNapasClient(NapasClient):
    """Mock Napas client that reads from the local DB for realistic data."""

    def verify_notice_signature(self, payload: bytes, signature: str) -> bool:
        """Always returns True in mock mode."""
        return True

    def get_settlement_report(self, report_date: date) -> list[SettlementRecord]:
        """Query DB for SETTLED/NOTIFIED/QUEUED/RECONCILED/DISPUTE transactions on report_date."""
        settled_states = {"SETTLED", "NOTIFIED", "QUEUED", "RECONCILED", "DISPUTE"}
        day_start = datetime.combine(report_date, datetime.min.time())
        day_end = day_start + timedelta(days=1)

        db = SessionLocal()
        try:
            txns = (
                db.query(Transaction)
                .filter(
                    Transaction.state.in_(settled_states),
                    Transaction.notice_acsc_at >= day_start,
                    Transaction.notice_acsc_at < day_end,
                )
                .all()
            )

            records: list[SettlementRecord] = []
            for txn in txns:
                records.append(
                    SettlementRecord(
                        full_order_id=txn.full_order_id,
                        merchant_id=txn.merchant_id,
                        amount=txn.amount,
                        settled_at=(
                            txn.notice_acsc_at.isoformat()
                            if txn.notice_acsc_at
                            else ""
                        ),
                        status="ACSC",
                    )
                )
            return records
        finally:
            db.close()

    def get_transaction_status(self, full_order_id: str) -> TxnStatusDTO:
        """Look up a transaction in the DB and return its status."""
        db = SessionLocal()
        try:
            txn = (
                db.query(Transaction)
                .filter(Transaction.full_order_id == full_order_id)
                .first()
            )
            if txn is None:
                raise ValueError(f"Transaction not found: {full_order_id}")

            return TxnStatusDTO(
                full_order_id=txn.full_order_id,
                status=txn.state,
                amount=txn.amount,
                merchant_id=txn.merchant_id,
                timestamp=txn.updated_at.isoformat() if txn.updated_at else "",
            )
        finally:
            db.close()
