from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TransactionOut(BaseModel):
    id: str
    full_order_id: str
    merchant_id: str
    amount: int
    state: str
    notice_acsp_at: Optional[datetime] = None
    notice_acsc_at: Optional[datetime] = None
    notified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TransactionListParams(BaseModel):
    merchant_id: Optional[str] = None
    state: Optional[str] = None
    date_from: Optional[str] = None  # dd/mm/yyyy
    date_to: Optional[str] = None
    page: int = 1
    page_size: int = 20
