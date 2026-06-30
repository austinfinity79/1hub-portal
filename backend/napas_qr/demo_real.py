"""Demo chuyển khoản THẬT qua VietQR IBFT — tới TK Vietcombank.

Sinh QR EMVCo chuẩn, app ngân hàng bất kỳ quét được và chuyển tiền THẬT.
Dùng để verify generator end-to-end mà không phụ thuộc alias NAPAS.

Khác biệt với production:
  - Demo điền BNB ID + số TK trực tiếp vào ID 38 (chuyển thẳng TK cá nhân).
  - Production thay số TK bằng alias NPxxx (TODO[NAPAS-Q2]).

Chạy:
    pip install "qrcode[pil]"
    python -m napas_qr.demo_real
"""

from napas_qr.builder import generate_dynamic_qr
from napas_qr.crc import crc16_ccitt
from napas_qr.tlv import parse_tlv

# Tham số thật — Vietcombank
BNB_ID = "970436"                # Vietcombank BIN (Phụ lục 2 APG)
CONSUMER_ID = "REDACTED_ACCOUNT"    # Số TK VCB thật
AMOUNT = 2000                    # Tối thiểu hạn mức APG, test mất ít tiền nhất
PURPOSE = "test napas qr"


def main() -> None:
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
        print("Quét bằng app ngân hàng -> chuyển 2.000d tới VCB REDACTED_ACCOUNT")
    except ImportError:
        print("Cài qrcode để sinh ảnh: pip install 'qrcode[pil]'")
        print("Hoặc copy chuỗi QR ở trên vào bất kỳ QR generator online.")


if __name__ == "__main__":
    main()
