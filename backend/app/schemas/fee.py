from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class FeeOut(BaseModel):
    id: str
    txn_id: str
    merchant_id: str
    fee_amount: int
    status: str  # PHAI_THU | DA_NHAN
    remitted_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}
