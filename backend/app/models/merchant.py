from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Merchant(Base):
    __tablename__ = "merchants"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # 1 = realtime, 2 = batch
    notify_mode: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    fee_flat: Mapped[int] = mapped_column(Integer, nullable=False)  # VND per txn
    bank_account: Mapped[str] = mapped_column(String(30), nullable=False)
    bank_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    transactions = relationship("Transaction", back_populates="merchant")
    fees = relationship("Fee", back_populates="merchant")
