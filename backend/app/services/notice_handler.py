from datetime import datetime

from sqlalchemy.orm import Session

from app.core.exceptions import AppException, DuplicateNoticeError, SignatureVerificationFailed
from app.core.idempotency import is_notice_processed
from app.core.security import verify_napas_signature
from app.models.transaction import Transaction
from app.repositories import fee_repo, merchant_repo, transaction_repo
from app.schemas.napas_notice import NapasNoticePayload
from app.services import notify_router
from app.services.txn_state import transition


def handle_notice(db: Session, payload: NapasNoticePayload) -> Transaction:
    """Xu ly notice tu Napas (ACSP/ACSC/RJCT).

    Toan bo logic trong 1 transaction DB duy nhat.
    """
    # 1. Xac thuc chu ky Napas
    if not verify_napas_signature(payload.model_dump_json().encode(), payload.signature):
        raise SignatureVerificationFailed()

    # 2. Kiem tra idempotency
    if is_notice_processed(db, payload.full_order_id, payload.status):
        raise DuplicateNoticeError(payload.full_order_id)

    # 3. Xu ly theo trang thai
    if payload.status == "ACSP":
        txn = _handle_acsp(db, payload)
    elif payload.status == "ACSC":
        txn = _handle_acsc(db, payload)
    else:
        txn = _handle_rjct(db, payload)

    db.commit()
    return txn


def _handle_acsp(db: Session, payload: NapasNoticePayload) -> Transaction:
    """ACSP: Napas da nhan lenh — chuyen sang AUTHORIZED."""
    txn = transaction_repo.get_by_order_id(db, payload.full_order_id)
    if not txn:
        txn = transaction_repo.create(
            db,
            full_order_id=payload.full_order_id,
            merchant_id=payload.merchant_id,
            amount=payload.amount,
            state="INITIATED",
        )
    return transition(db, txn, "AUTHORIZED", notice_acsp_at=datetime.utcnow())


def _handle_acsc(db: Session, payload: NapasNoticePayload) -> Transaction:
    """ACSC: Napas da thanh toan — chuyen sang SETTLED, tao phi, gui thong bao."""
    txn = transaction_repo.get_by_order_id(db, payload.full_order_id)
    if not txn:
        raise AppException(404, f"Transaction not found: {payload.full_order_id}")

    txn = transition(db, txn, "SETTLED", notice_acsc_at=datetime.utcnow())

    # Tao ban ghi phi
    merchant = merchant_repo.get_by_id(db, txn.merchant_id)
    if not merchant:
        raise AppException(404, f"Merchant not found: {txn.merchant_id}")
    fee_repo.create(db, txn.id, merchant.id, merchant.fee_flat)

    # Dinh tuyen thong bao cho merchant
    notify_router.route_notification(db, txn, merchant)

    return txn


def _handle_rjct(db: Session, payload: NapasNoticePayload) -> Transaction:
    """RJCT: Napas tu choi — chuyen sang REJECTED."""
    txn = transaction_repo.get_by_order_id(db, payload.full_order_id)
    if not txn:
        txn = transaction_repo.create(
            db,
            full_order_id=payload.full_order_id,
            merchant_id=payload.merchant_id,
            amount=payload.amount,
            state="INITIATED",
        )
    return transition(db, txn, "REJECTED")
