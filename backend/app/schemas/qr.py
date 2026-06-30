"""Schemas for QR generation endpoint."""

from pydantic import BaseModel


class QrGenerateRequest(BaseModel):
    merchant_id: str
    amount: int
    reference: str | None = None
    purpose: str | None = None


class QrGenerateResponse(BaseModel):
    qr_string: str
    amount: int
    reference: str | None = None
    purpose: str | None = None
