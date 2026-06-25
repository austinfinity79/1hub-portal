from pydantic import BaseModel, Field
from typing import Literal


class NapasNoticePayload(BaseModel):
    """Payload webhook tu Napas. TODO[NAPAS]: cap nhat khi co spec that."""

    full_order_id: str = Field(..., description="Ma don hang Napas")
    merchant_id: str
    amount: int  # VND
    status: Literal["ACSP", "ACSC", "RJCT"]
    signature: str = Field(..., description="Chu ky Napas de verify")
    timestamp: str  # ISO datetime
