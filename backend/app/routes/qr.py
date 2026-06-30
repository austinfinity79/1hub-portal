"""QR generation routes — sinh chuỗi VietQR IBFT động cho merchant."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.merchant import Merchant
from app.schemas.qr import QrGenerateRequest, QrGenerateResponse
from napas_qr.builder import generate_dynamic_qr

router = APIRouter(prefix="/api/qr", tags=["QR"])

# TODO[NAPAS-Q2]: BNB ID thật chờ NAPAS cấp. Hiện dùng giá trị mẫu.
_DEFAULT_BNB_ID = "970403"
# TODO[NAPAS-Q2]: Consumer ID format chờ xác nhận. Hiện dùng bank_account của merchant.


@router.post("/generate", response_model=QrGenerateResponse)
def generate_qr(
    body: QrGenerateRequest,
    db: Session = Depends(get_db),
) -> QrGenerateResponse:
    """Sinh chuỗi VietQR IBFT động cho một đơn hàng.

    Dùng bank_account của merchant làm consumer_id (tạm thời).
    """
    merchant = db.query(Merchant).filter(Merchant.id == body.merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")

    try:
        qr_string = generate_dynamic_qr(
            bnb_id=_DEFAULT_BNB_ID,
            consumer_id=merchant.bank_account,
            amount=body.amount,
            service="QRIBFTTA",
            reference=body.reference,
            purpose=body.purpose,
            merchant_name=merchant.name,
            merchant_city="Ho Chi Minh",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return QrGenerateResponse(
        qr_string=qr_string,
        amount=body.amount,
        reference=body.reference,
        purpose=body.purpose,
    )
