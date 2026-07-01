"""Demo chuyển khoản THẬT qua VietQR IBFT.

Sinh QR EMVCo chuẩn, app ngân hàng bất kỳ quét được và chuyển tiền THẬT.
Dùng để verify generator end-to-end mà không phụ thuộc alias NAPAS.

Khác biệt với production:
  - Demo điền BNB ID + số TK trực tiếp vào ID 38 (chuyển thẳng TK cá nhân).
  - Production thay số TK bằng alias NPxxx (TODO[NAPAS-Q2]).

Cấu hình qua env hoặc sửa trực tiếp giá trị bên dưới.

Chạy:
    pip install "qrcode[pil]"
    DEMO_BNB_ID=970436 DEMO_CONSUMER_ID=<số TK> python -m napas_qr.demo_real
"""

import os

from napas_qr.builder import generate_dynamic_qr
from napas_qr.crc import crc16_ccitt
from napas_qr.tlv import parse_tlv

# Đọc từ env — KHÔNG hardcode số TK cá nhân
BNB_ID = os.environ.get("DEMO_BNB_ID", "970436")          # BIN ngân hàng (mặc định Vietcombank)
CONSUMER_ID = os.environ.get("DEMO_CONSUMER_ID", "")       # Số TK đích — bắt buộc set qua env
AMOUNT = int(os.environ.get("DEMO_AMOUNT", "2000"))         # Tối thiểu hạn mức APG
PURPOSE = os.environ.get("DEMO_PURPOSE", "test napas qr")


def main() -> None:
    if not CONSUMER_ID:
        print("ERROR: Set DEMO_CONSUMER_ID env variable (số TK ngân hàng đích)")
        print("  DEMO_CONSUMER_ID=0123456789 python -m napas_qr.demo_real")
        return

    s = generate_dynamic_qr(
        bnb_id=BNB_ID,
        consumer_id=CONSUMER_ID,
        amount=AMOUNT,
        service="QRIBFTTA",
        purpose=PURPOSE,
    )

    print("=== DEMO REAL VietQR IBFT ===")
    print(f"QR string: {s}")
    print(f"CRC tail:  {s[-4:]}")
    print(f"Length:     {len(s)} chars")
    print()

    # Verify CRC
    payload = s[:-4]
    crc = crc16_ccitt(payload)
    assert crc == s[-4:], f"CRC mismatch: computed {crc}, in string {s[-4:]}"
    print(f"CRC verify: OK ({crc})")

    # Parse và hiển thị fields
    fields = dict(parse_tlv(s))
    print(f"Amount:     {fields['54']} VND")
    id38 = dict(parse_tlv(fields["38"]))
    sub01 = dict(parse_tlv(id38["01"]))
    print(f"BNB ID:     {sub01['00']}")
    print(f"Account:    {sub01['01']}")
    print(f"Service:    {id38['02']}")
    print()

    # Sinh QR image
    try:
        import qrcode
        qrcode.make(s).save("demo_real.png")
        print("QR image saved: demo_real.png")
        print("Quét bằng app ngân hàng để test")
    except ImportError:
        print("Cài qrcode để sinh ảnh: pip install 'qrcode[pil]'")
        print("Hoặc copy chuỗi QR ở trên vào bất kỳ QR generator online.")


if __name__ == "__main__":
    main()
