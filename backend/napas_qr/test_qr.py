"""Test cases đối chiếu spec NAPAS QR Format v2.0.

Chạy: pytest napas_qr/test_qr.py -v
"""

import pytest

from napas_qr.crc import crc16_ccitt
from napas_qr.tlv import tlv, parse_tlv
from napas_qr.validators import validate_amount
from napas_qr.builder import (
    build_id38,
    build_id62,
    generate_dynamic_qr,
)


# ── Test 1: CRC §5.1 ───────────────────────────────────────────────

class TestCRC:
    def test_crc_section_5_1(self):
        """§5.1: CRC trên chuỗi tĩnh → F4E5."""
        inp = (
            "00020101021138570010A000000727"
            "01270006970403011200110123456780208QRIBFTTA"
            "53037045802VN6304"
        )
        assert crc16_ccitt(inp) == "F4E5"

    def test_crc_section_5_3_spec_raw(self):
        """§5.3: CRC trên raw spec string (có TLV length typo ở sub 38.01.01).

        Spec in §5.1 dùng string có sub 01 length = "12" nhưng value 13 ký tự.
        Đây là typo trong spec; CRC vẫn đúng trên string đó.
        Ta verify CRC function hoạt động đúng trên bất kỳ input nào.
        """
        # Chuỗi spec §5.1 (tĩnh, Initiation=11) đã test ở trên → F4E5
        # Ở đây test thêm CRC trên output thực tế của builder (TLV đúng)
        from napas_qr.builder import generate_dynamic_qr
        qr = generate_dynamic_qr(
            bnb_id="970403",
            consumer_id="0011012345678",
            amount=180000,
            reference="YYYYYYYYYY",
            purpose="thanh toan abc",
        )
        payload = qr[:-4]  # strip CRC value, giữ "6304"
        assert payload.endswith("6304")
        assert crc16_ccitt(payload) == qr[-4:]  # CRC tự nhất quán


# ── Test 2: TLV ─────────────────────────────────────────────────────

class TestTLV:
    def test_tlv_basic(self):
        assert tlv("00", "01") == "000201"
        assert tlv("53", "704") == "5303704"
        assert tlv("58", "VN") == "5802VN"

    def test_tlv_length_padding(self):
        """Length phải luôn 2 chữ số, zero-pad."""
        assert tlv("54", "180000") == "5406180000"

    def test_parse_roundtrip(self):
        data = tlv("00", "01") + tlv("01", "12") + tlv("58", "VN")
        parsed = parse_tlv(data)
        assert parsed == [("00", "01"), ("01", "12"), ("58", "VN")]

    def test_parse_nested(self):
        """Parse block ID 38 nested structure."""
        inner = tlv("00", "970403") + tlv("01", "00110123456789")
        outer = tlv("01", inner)
        parsed = parse_tlv(outer)
        assert len(parsed) == 1
        tag, value = parsed[0]
        assert tag == "01"
        # Parse nested
        nested = parse_tlv(value)
        assert nested == [("00", "970403"), ("01", "00110123456789")]


# ── Test 3: Build §5.3 full string match ─────────────────────────────

class TestBuildFullString:
    def test_section_5_3_dynamic_qr(self):
        """Build chuỗi QR động IBFT với tham số tương tự §5.3.

        Spec §5.1/5.3 có TLV length typo (sub 38.01.01 ghi "12" nhưng value
        13 ký tự). Builder của ta sinh TLV đúng chuẩn (length = 13).
        Verify từng thành phần thay vì so string spec nguyên văn.
        """
        # Block 38: verify nested TLV đúng
        id38 = build_id38("970403", "0011012345678")
        # sub 01.01 length = 13 (đúng cho "0011012345678")
        assert "011300110123456780208QRIBFTTA" in id38
        # tổng length ID 38 = 57
        assert id38.startswith("3857")

        # Build toàn bộ
        result = generate_dynamic_qr(
            bnb_id="970403",
            consumer_id="0011012345678",
            amount=180000,
            reference="YYYYYYYYYY",
            purpose="thanh toan abc",
        )

        # Verify structure
        assert result.startswith("000201")           # Payload Format = 01
        assert "010212" in result                     # Initiation = 12 (dynamic)
        assert "5303704" in result                    # Currency = VND
        assert "5406180000" in result                 # Amount = 180000
        assert "5802VN" in result                     # Country = VN
        assert "0510YYYYYYYYYY" in result             # Reference Label
        assert "0814thanh toan abc" in result         # Purpose
        assert result[-8:-4] == "6304"                # CRC tag + length
        # CRC tự nhất quán
        payload = result[:-4]
        assert crc16_ccitt(payload) == result[-4:]


# ── Test 4: Amount validation ─────────────────────────────────────────

class TestAmountValidation:
    def test_valid_amounts(self):
        assert validate_amount(50000) == "50000"
        assert validate_amount("180000") == "180000"
        assert validate_amount(2000) == "2000"
        assert validate_amount(499999999) == "499999999"

    def test_amount_with_trailing_dot_zero(self):
        """VND .0 thập phân cho phép (= 0)."""
        assert validate_amount("50000.0") == "50000"
        assert validate_amount("50000.00") == "50000"

    def test_reject_space_separator(self):
        with pytest.raises(ValueError, match="chỉ chấp nhận"):
            validate_amount("50 000")

    def test_reject_zero(self):
        with pytest.raises(ValueError, match="khác 0"):
            validate_amount(0)

    def test_reject_below_min(self):
        with pytest.raises(ValueError, match="dưới hạn mức"):
            validate_amount(1999)

    def test_reject_above_max(self):
        with pytest.raises(ValueError, match="vượt hạn mức"):
            validate_amount(500_000_000)

    def test_reject_decimal(self):
        """VND không có phần thập phân khác 0."""
        with pytest.raises(ValueError, match="thập phân"):
            validate_amount("50000.5")

    def test_reject_comma_separator(self):
        with pytest.raises(ValueError, match="chỉ chấp nhận"):
            validate_amount("50,000")


# ── Test 5: Round-trip parse ──────────────────────────────────────────

class TestRoundTrip:
    def test_parse_generated_qr(self):
        """Build → parse → verify fields khớp input."""
        qr = generate_dynamic_qr(
            bnb_id="970403",
            consumer_id="0011012345678",
            amount=250000,
            reference="ORD-001",
            purpose="cafe pho",
        )

        # Parse top-level TLV (bỏ 4 ký tự CRC cuối khi parse)
        # Vì CRC value nằm trong field 63, parse bình thường
        fields = dict(parse_tlv(qr))

        assert fields["00"] == "01"           # Payload Format
        assert fields["01"] == "12"           # Dynamic
        assert fields["53"] == "704"          # VND
        assert fields["54"] == "250000"       # Amount
        assert fields["58"] == "VN"           # Country

        # Parse block 38 nested
        id38_fields = dict(parse_tlv(fields["38"]))
        assert id38_fields["00"] == "A000000727"  # NAPAS GUID
        assert id38_fields["02"] == "QRIBFTTA"    # Service code

        # Parse sub 01 (payment network)
        sub01 = dict(parse_tlv(id38_fields["01"]))
        assert sub01["00"] == "970403"            # BNB ID
        assert sub01["01"] == "0011012345678"     # Consumer ID

        # Parse block 62 nested
        id62_fields = dict(parse_tlv(fields["62"]))
        assert id62_fields["05"] == "ORD-001"     # Reference
        assert id62_fields["08"] == "cafe pho"    # Purpose

        # Verify CRC
        assert fields["63"] is not None
        crc_value = fields["63"]
        assert len(crc_value) == 4
        # Recompute CRC on everything up to and including "6304"
        payload_for_crc = qr[:-4]  # strip CRC value
        assert crc16_ccitt(payload_for_crc) == crc_value

    def test_optional_fields_omitted(self):
        """Khi không có reference/purpose, block 62 không xuất hiện."""
        qr = generate_dynamic_qr(
            bnb_id="970403",
            consumer_id="0011012345678",
            amount=50000,
        )
        fields = dict(parse_tlv(qr))
        assert "62" not in fields

    def test_with_merchant_info(self):
        """ID 59 + 60 xuất hiện khi truyền merchant_name/city."""
        qr = generate_dynamic_qr(
            bnb_id="970403",
            consumer_id="0011012345678",
            amount=100000,
            merchant_name="CafePho 68",
            merchant_city="Ho Chi Minh",
        )
        fields = dict(parse_tlv(qr))
        assert fields["59"] == "CafePho 68"
        assert fields["60"] == "Ho Chi Minh"
