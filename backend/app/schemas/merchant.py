from pydantic import BaseModel
from datetime import datetime


class MerchantBase(BaseModel):
    name: str
    notify_mode: int  # 1=realtime, 2=batch
    fee_flat: int  # VND per txn
    bank_account: str
    bank_name: str


class MerchantOut(MerchantBase):
    id: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
