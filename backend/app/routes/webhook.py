"""Webhook routes for receiving Napas payment notices."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.napas_notice import NapasNoticePayload
from app.schemas.transaction import TransactionOut
from app.services import notice_handler

router = APIRouter(prefix="/webhook", tags=["Webhook"])


@router.post("/napas/notice", response_model=TransactionOut)
def receive_napas_notice(
    payload: NapasNoticePayload,
    db: Session = Depends(get_db),
) -> TransactionOut:
    """Receive a payment notice from Napas.

    Business exceptions (DuplicateNoticeError, SignatureVerificationFailed,
    InvalidStateTransition) are handled by the global exception handler.
    """
    txn = notice_handler.handle_notice(db, payload)
    return TransactionOut.model_validate(txn)
