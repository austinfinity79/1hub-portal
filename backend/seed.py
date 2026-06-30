"""Seed script for 1Hub Control Portal development database.

Drops and recreates all tables, then populates with realistic Vietnamese
merchant and transaction data across all states.

Usage:
    python seed.py
"""

import random
from datetime import datetime, timedelta
from uuid import uuid4

from app.core.auth import hash_password
from app.database import Base, SessionLocal, engine
from app.models.fee import Fee
from app.models.merchant import Merchant
from app.models.notify_queue import NotifyQueue
from app.models.reconciliation import Reconciliation
from app.models.transaction import Transaction
from app.models.user import User


def _uuid() -> str:
    return str(uuid4())


def _order_id() -> str:
    return f"NAPAS-{uuid4().hex[:8].upper()}"


def _random_amount() -> int:
    """Return a realistic VND amount (rounded to 1000)."""
    return random.randrange(50_000, 5_000_001, 1_000)


def _hours_ago(hours: int) -> datetime:
    return datetime.utcnow() - timedelta(hours=hours)


def _days_ago(days: int, hour: int = 10) -> datetime:
    return (datetime.utcnow() - timedelta(days=days)).replace(
        hour=hour, minute=random.randint(0, 59), second=random.randint(0, 59)
    )


def seed() -> None:
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # ── Default Admin User ────────────────────────────────────
        admin = User(
            id=_uuid(),
            username="admin",
            email="admin@1hub.vn",
            hashed_password=hash_password("admin123"),
            role="admin",
            is_active=True,
        )
        db.add(admin)
        db.flush()
        print("  Created default admin user (admin / admin123)")

        # ── Merchants ──────────────────────────────────────────────
        merchants_data = [
            {
                "name": "CafePho 68",
                "notify_mode": 1,
                "fee_flat": 1500,
                "bank_account": "0071000123456",
                "bank_name": "Vietcombank",
            },
            {
                "name": "BookStore Online",
                "notify_mode": 2,
                "fee_flat": 2000,
                "bank_account": "19033456789012",
                "bank_name": "Techcombank",
            },
            {
                "name": "GadgetVN",
                "notify_mode": 1,
                "fee_flat": 1800,
                "bank_account": "0801234567890",
                "bank_name": "MB Bank",
            },
        ]

        merchants: list[Merchant] = []
        for md in merchants_data:
            m = Merchant(id=_uuid(), status="ACTIVE", **md)
            db.add(m)
            merchants.append(m)
        db.flush()

        m_cafe, m_book, m_gadget = merchants
        print(f"  Created {len(merchants)} merchants")

        # ── Helper to pick a merchant ──────────────────────────────
        def pick_merchant() -> Merchant:
            return random.choice(merchants)

        # ── Transactions ───────────────────────────────────────────
        transactions: list[Transaction] = []
        fees_created = 0
        queues_created = 0
        recon_created = 0

        def make_txn(
            state: str,
            merchant: Merchant | None = None,
            **extra: object,
        ) -> Transaction:
            m = merchant or pick_merchant()
            txn = Transaction(
                id=_uuid(),
                full_order_id=_order_id(),
                merchant_id=m.id,
                amount=_random_amount(),
                state=state,
                created_at=_days_ago(random.randint(0, 6)),
                **extra,
            )
            db.add(txn)
            transactions.append(txn)
            return txn

        # 3 INITIATED
        for _ in range(3):
            make_txn("INITIATED")

        # 4 AUTHORIZED (have notice_acsp_at)
        for _ in range(4):
            make_txn(
                "AUTHORIZED",
                notice_acsp_at=_hours_ago(random.randint(2, 48)),
            )

        # 5 SETTLED (have both acsp + acsc)
        for _ in range(5):
            acsp = _hours_ago(random.randint(50, 120))
            acsc = acsp + timedelta(hours=random.randint(1, 12))
            make_txn(
                "SETTLED",
                notice_acsp_at=acsp,
                notice_acsc_at=acsc,
            )

        # 3 NOTIFIED (settled + notified_at)
        for _ in range(3):
            acsp = _hours_ago(random.randint(70, 150))
            acsc = acsp + timedelta(hours=random.randint(1, 8))
            notified = acsc + timedelta(minutes=random.randint(5, 120))
            make_txn(
                "NOTIFIED",
                merchant=m_cafe,  # mode-1 merchant gets realtime notify
                notice_acsp_at=acsp,
                notice_acsc_at=acsc,
                notified_at=notified,
            )

        # 2 QUEUED (for mode-2 merchant BookStore Online)
        queued_txns: list[Transaction] = []
        for _ in range(2):
            acsp = _hours_ago(random.randint(20, 60))
            acsc = acsp + timedelta(hours=random.randint(1, 6))
            txn = make_txn(
                "QUEUED",
                merchant=m_book,
                notice_acsp_at=acsp,
                notice_acsc_at=acsc,
            )
            queued_txns.append(txn)

        # 1 RECONCILED
        acsp = _days_ago(3, 9)
        acsc = acsp + timedelta(hours=4)
        recon_txn = make_txn(
            "RECONCILED",
            notice_acsp_at=acsp,
            notice_acsc_at=acsc,
            notified_at=acsc + timedelta(minutes=30),
        )

        # 1 DISPUTE
        acsp = _days_ago(4, 11)
        acsc = acsp + timedelta(hours=3)
        dispute_txn = make_txn(
            "DISPUTE",
            notice_acsp_at=acsp,
            notice_acsc_at=acsc,
            notified_at=acsc + timedelta(minutes=45),
        )

        # 1 REJECTED
        make_txn("REJECTED")

        db.flush()
        print(f"  Created {len(transactions)} transactions")

        # ── Fees ───────────────────────────────────────────────────
        # Create Fee for every SETTLED/NOTIFIED/QUEUED/RECONCILED/DISPUTE txn
        fee_states = {"SETTLED", "NOTIFIED", "QUEUED", "RECONCILED", "DISPUTE"}
        fee_txns = [t for t in transactions if t.state in fee_states]
        da_nhan_count = 0

        for i, txn in enumerate(fee_txns):
            # Find the merchant's fee_flat
            merchant = next(m for m in merchants if m.id == txn.merchant_id)
            fee = Fee(
                id=_uuid(),
                txn_id=txn.id,
                merchant_id=txn.merchant_id,
                fee_amount=merchant.fee_flat,
                status="PHAI_THU",
            )
            # Mark 3 fees as DA_NHAN
            if i < 3:
                fee.status = "DA_NHAN"
                fee.remitted_at = datetime.utcnow() - timedelta(
                    hours=random.randint(1, 24)
                )
                da_nhan_count += 1
            db.add(fee)
            fees_created += 1

        db.flush()
        print(
            f"  Created {fees_created} fees "
            f"({da_nhan_count} DA_NHAN, {fees_created - da_nhan_count} PHAI_THU)"
        )

        # ── Reconciliation ─────────────────────────────────────────
        # RECONCILED txn -> KHOP
        recon_date = (datetime.utcnow() - timedelta(days=1)).date()
        rec_khop = Reconciliation(
            id=_uuid(),
            recon_date=recon_date,
            txn_id=recon_txn.id,
            ledger_amount=recon_txn.amount,
            napas_amount=recon_txn.amount,  # matching
            result="KHOP",
        )
        db.add(rec_khop)
        recon_created += 1

        # DISPUTE txn -> LECH (napas_amount differs)
        diff = random.choice([500, -500, 1000, -1000, 2500])
        rec_lech = Reconciliation(
            id=_uuid(),
            recon_date=recon_date,
            txn_id=dispute_txn.id,
            ledger_amount=dispute_txn.amount,
            napas_amount=dispute_txn.amount + diff,
            result="LECH",
        )
        db.add(rec_lech)
        recon_created += 1
        db.flush()
        print(f"  Created {recon_created} reconciliation records (1 KHOP, 1 LECH)")

        # ── NotifyQueue ────────────────────────────────────────────
        for txn in queued_txns:
            nq = NotifyQueue(
                id=_uuid(),
                txn_id=txn.id,
                merchant_id=txn.merchant_id,
                batched_at=None,
            )
            db.add(nq)
            queues_created += 1

        db.flush()
        print(f"  Created {queues_created} notify queue entries (pending)")

        # ── Commit ─────────────────────────────────────────────────
        db.commit()
        print("\nSeed completed successfully!")
        print(f"  Merchants:       {len(merchants)}")
        print(f"  Transactions:    {len(transactions)}")
        print(f"  Fees:            {fees_created}")
        print(f"  Reconciliations: {recon_created}")
        print(f"  Notify Queue:    {queues_created}")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
