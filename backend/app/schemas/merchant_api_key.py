from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ApiKeyCreate(BaseModel):
    merchant_id: str
    label: str


class ApiKeyOut(BaseModel):
    id: str
    merchant_id: str
    label: str
    key_prefix: str
    is_active: bool
    created_by: str
    created_at: datetime
    last_used_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ApiKeyCreatedOut(ApiKeyOut):
    """Returned only at creation time — contains the full plaintext key."""
    full_key: str


class ApiKeyRevealRequest(BaseModel):
    password: str


class ApiKeyRevealResponse(BaseModel):
    key: str
