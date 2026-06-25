from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    full_order_id: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )
    merchant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("merchants.id"), nullable=False
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # VND
    # Trạng thái: INITIATED -> AUTHORIZED -> SETTLED -> NOTIFIED -> QUEUED -> RECONCILED
    #             hoặc DISPUTE / REJECTED
    state: Mapped[str] = mapped_column(
        String(20), nullable=False, default="INITIATED"
    )
    notice_acsp_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    notice_acsc_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    notified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    merchant = relationship("Merchant", back_populates="transactions")

    __table_args__ = (
        Index("ix_transactions_merchant_state", "merchant_id", "state"),
        Index("ix_transactions_created_at", "created_at"),
    )
