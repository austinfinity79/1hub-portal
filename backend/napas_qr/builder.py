"""VietQR IBFT Dynamic QR builder theo NAPAS Phần VII QR Format v2.0.

Hàm chính: generate_dynamic_qr() trả chuỗi QR payload đã gắn CRC,
sẵn sàng nhét vào QR image (render ở layer khác).

# TODO[NAPAS-Q2]: Xác nhận cách map định danh 1Hub vào block ID 38.
#   - bnb_id (6 ký tự) = mã BIN NHHT do NAPAS cấp.
#   - consumer_id (≤19 ký tự) = alias hoặc số TK đích.
#   Hiện tham số hóa, không hardcode.
"""

from napas_qr.crc import crc16_ccitt
from napas_qr.tlv import tlv
from napas_qr.validators import validate_amount, validate_ans

# Hằng số chuẩn NAPAS
_PAYLOAD_FORMAT = "01"          # §4.2.1 — version 01
_INITIATION_DYNAMIC = "12"     # §4.2.2 — QR động, dùng 1 lần
_NAPAS_GUID = "A000000727"     # §4.2.3.2 — AID NAPAS
_CURRENCY_VND = "704"          # §4.2.5 — ISO 4217 VND
_COUNTRY_VN = "VN"             # §4.2.13 — ISO 3166-1 alpha-2
_CRC_TAG = "63"                # §4.2.15
_CRC_PLACEHOLDER = "6304"      # tag + length(04), value tính sau


def build_id38(
    bnb_id: str,
    consumer_id: str,
    service: str = "QRIBFTTA",
) -> str:
    """Build block ID 38 — Consumer Account Information (§4.2.3.2, Bảng 4).

    Sub-fields:
        00 — GUID: A000000727 (NAPAS AID, cố định)
        01 — Payment network: nested TLV gồm:
              00 — BNB ID (6 ký tự, mã BIN NHHT)
              01 — Consumer/Merchant Account (ANS ≤19)
        02 — Service code: QRIBFTTA (đến tài khoản) hoặc QRIBFTTC (đến thẻ)

    # TODO[NAPAS-Q2]: Giá trị bnb_id + consumer_id phụ thuộc NAPAS trả lời.
    """
    validate_ans(bnb_id, 6, "BNB ID (ID 38.01.00)")
    validate_ans(consumer_id, 19, "Consumer ID (ID 38.01.01)")

    if service not in ("QRIBFTTA", "QRIBFTTC"):
        raise ValueError(f"Service code phải là QRIBFTTA hoặc QRIBFTTC, nhận: {service!r}")

    # Nested TLV cho sub 01 (Payment network)
    sub01_inner = tlv("00", bnb_id) + tlv("01", consumer_id)
    # Build toàn bộ block 38
    block = tlv("00", _NAPAS_GUID) + tlv("01", sub01_inner) + tlv("02", service)
    return tlv("38", block)


def build_id62(
    reference: str | None = None,
    purpose: str | None = None,
) -> str:
    """Build block ID 62 — Additional Data Field Template (§4.2.14, Bảng 8).

    Sub-fields (chỉ gồm nếu không None):
        05 — Reference Label (ANS ≤25): mã tham chiếu / order ID
        08 — Purpose of Transaction (ANS ≤25): nội dung thanh toán

    Tổng value ID 62 ≤ 99 ký tự.
    """
    parts: list[str] = []

    if reference is not None:
        validate_ans(reference, 25, "Reference Label (ID 62.05)")
        parts.append(tlv("05", reference))

    if purpose is not None:
        validate_ans(purpose, 25, "Purpose (ID 62.08)")
        parts.append(tlv("08", purpose))

    if not parts:
        return ""

    inner = "".join(parts)
    if len(inner) > 99:
        raise ValueError(
            f"Block ID 62 quá dài: {len(inner)} ký tự (max 99)"
        )
    return tlv("62", inner)


def generate_dynamic_qr(
    bnb_id: str,
    consumer_id: str,
    amount: int | str,
    service: str = "QRIBFTTA",
    reference: str | None = None,
    purpose: str | None = None,
    merchant_name: str | None = None,   # ID 59, ANS ≤ 25
    merchant_city: str | None = None,   # ID 60, ANS ≤ 15
) -> str:
    """Sinh chuỗi VietQR IBFT động, đã gắn CRC.

    Args:
        bnb_id: Mã BIN ngân hàng thụ hưởng (6 ký tự).
            # TODO[NAPAS-Q2]: giá trị thật chờ NAPAS cấp.
        consumer_id: Alias/account đích (≤19 ký tự).
            # TODO[NAPAS-Q2]: format chờ NAPAS xác nhận.
        amount: Số tiền VND (int hoặc str), trong hạn mức APG.
        service: Mã dịch vụ — "QRIBFTTA" (đến TK) hoặc "QRIBFTTC" (đến thẻ).
        reference: Mã tham chiếu / order ID (≤25 ký tự).
        purpose: Nội dung thanh toán (≤25 ký tự).
        merchant_name: Tên merchant (§4.2.11, ANS ≤25).
        merchant_city: Thành phố (§4.2.12, ANS ≤15).

    Returns:
        Chuỗi QR payload hoàn chỉnh (kết thúc bằng 4 ký tự CRC hex).

    Raises:
        ValueError: Input không hợp lệ.
    """
    amount_str = validate_amount(amount)

    # Build từng field theo đúng thứ tự ID tăng dần (§4.1)
    parts: list[str] = []

    # ID 00 — Payload Format Indicator (M)
    parts.append(tlv("00", _PAYLOAD_FORMAT))

    # ID 01 — Point of Initiation Method (M, 12 = động)
    parts.append(tlv("01", _INITIATION_DYNAMIC))

    # ID 38 — Consumer Account Information / NAPAS block (M)
    parts.append(build_id38(bnb_id, consumer_id, service))

    # ID 53 — Transaction Currency (M)
    parts.append(tlv("53", _CURRENCY_VND))

    # ID 54 — Transaction Amount (C — động thì có)
    parts.append(tlv("54", amount_str))

    # ID 58 — Country Code (M)
    parts.append(tlv("58", _COUNTRY_VN))

    # ID 59 — Merchant Name (O, §4.2.11)
    if merchant_name is not None:
        validate_ans(merchant_name, 25, "Merchant Name (ID 59)")
        parts.append(tlv("59", merchant_name))

    # ID 60 — Merchant City (O, §4.2.12)
    if merchant_city is not None:
        validate_ans(merchant_city, 15, "Merchant City (ID 60)")
        parts.append(tlv("60", merchant_city))

    # ID 62 — Additional Data Field Template (C)
    id62 = build_id62(reference=reference, purpose=purpose)
    if id62:
        parts.append(id62)

    # ID 63 — CRC (M, luôn cuối cùng)
    payload_without_crc = "".join(parts) + _CRC_PLACEHOLDER
    crc = crc16_ccitt(payload_without_crc)

    return payload_without_crc + crc
