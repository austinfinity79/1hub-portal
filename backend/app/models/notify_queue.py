from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class NotifyQueue(Base):
    __tablename__ = "notify_queue"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    txn_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("transactions.id"), nullable=False
    )
    merchant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("merchants.id"), nullable=False
    )
    queued_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    # NULL = chưa gửi batch, có giá trị = đã gửi batch
    batched_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
