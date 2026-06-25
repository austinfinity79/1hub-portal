from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Fee(Base):
    __tablename__ = "fees"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    txn_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("transactions.id"), unique=True, nullable=False
    )
    merchant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("merchants.id"), nullable=False
    )
    fee_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    # Trạng thái phí: PHAI_THU (chưa thu) hoặc DA_THU (đã thu)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="PHAI_THU"
    )
    remitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    merchant = relationship("Merchant", back_populates="fees")
