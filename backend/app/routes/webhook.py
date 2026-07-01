"""Webhook routes for receiving Napas payment notices.

IP whitelist: chỉ nhận từ NAPAS source IP (103.9.4.46 sandbox).
Bỏ qua khi ENV=dev. Config qua NAPAS_ALLOWED_IPS.
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.security import verify_napas_source_ip
from app.database import get_db
from app.schemas.napas_notice import NapasNoticePayload
from app.schemas.transaction import TransactionOut
from app.services import notice_handler

router = APIRouter(prefix="/webhook", tags=["Webhook"])


@router.post("/napas/notice", response_model=TransactionOut)
def receive_napas_notice(
    request: Request,
    payload: NapasNoticePayload,
    db: Session = Depends(get_db),
) -> TransactionOut:
    """Receive a payment notice from Napas.

    Security layers:
      1. IP whitelist (NAPAS source IP)
      2. Signature verification (RSA SHA256withRSA) — TODO[NAPAS-B1]
      3. Idempotency (duplicate notice check)

    Business exceptions (DuplicateNoticeError, SignatureVerificationFailed,
    InvalidStateTransition) are handled by the global exception handler.
    """
    verify_napas_source_ip(request)
    txn = notice_handler.handle_notice(db, payload)
    return TransactionOut.model_validate(txn)
