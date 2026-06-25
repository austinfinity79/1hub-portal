from pydantic import BaseModel
from datetime import date, datetime


class ReconciliationOut(BaseModel):
    id: str
    recon_date: date
    txn_id: str
    ledger_amount: int
    napas_amount: int
    result: str  # KHOP | LECH
    created_at: datetime

    model_config = {"from_attributes": True}
