from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Reconciliation(Base):
    __tablename__ = "reconciliations"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    recon_date: Mapped[date] = mapped_column(Date, nullable=False)
    txn_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("transactions.id"), nullable=False
    )
    ledger_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    napas_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    # Kết quả đối soát: KHOP (khớp) hoặc LECH (lệch)
    result: Mapped[str] = mapped_column(String(10), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    __table_args__ = (
        UniqueConstraint("recon_date", "txn_id", name="uq_recon_date_txn"),
    )
