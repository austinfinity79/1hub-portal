"""Validation rules theo NAPAS QR Format v2.0.

- Amount: chỉ [0-9], không phần thập phân cho VND, trong hạn mức APG.
- Length: ANS fields không vượt max theo Bảng spec.
"""

# Hạn mức APG hiện hành (VND)
APG_MIN_AMOUNT = 2_000
APG_MAX_AMOUNT = 499_999_999


def validate_amount(amount: int | str) -> str:
    """Validate và chuẩn hóa số tiền VND.

    VND không có phần thập phân (§4.2.6).
    Trả về chuỗi chỉ chứa [0-9], không padding.

    Raises:
        ValueError: amount sai format hoặc ngoài hạn mức.
    """
    raw = str(amount).strip()

    # Không cho phân cách nghìn hoặc ký tự lạ
    if not raw.replace(".", "").isdigit():
        raise ValueError(
            f"Amount chỉ chấp nhận [0-9] và tối đa 1 dấu '.': {raw!r}"
        )

    # Đếm dấu chấm
    if raw.count(".") > 1:
        raise ValueError(f"Amount có nhiều hơn 1 dấu '.': {raw!r}")

    # VND không có phần thập phân — nếu có dấu . thì phần sau phải là 0
    if "." in raw:
        integer_part, decimal_part = raw.split(".")
        if decimal_part and int(decimal_part) != 0:
            raise ValueError(
                f"VND không có phần thập phân: {raw!r}"
            )
        raw = integer_part

    value = int(raw)
    if value == 0:
        raise ValueError("Amount phải khác 0")
    if value < APG_MIN_AMOUNT:
        raise ValueError(
            f"Amount {value:,}đ dưới hạn mức tối thiểu APG ({APG_MIN_AMOUNT:,}đ)"
        )
    if value > APG_MAX_AMOUNT:
        raise ValueError(
            f"Amount {value:,}đ vượt hạn mức tối đa APG ({APG_MAX_AMOUNT:,}đ)"
        )
    return str(value)


def validate_ans(value: str, max_length: int, field_name: str) -> str:
    """Validate chuỗi ANS (Alphanumeric Special) theo spec.

    Raises:
        ValueError: Nếu vượt max_length.
    """
    if len(value) > max_length:
        raise ValueError(
            f"{field_name} quá dài: {len(value)} ký tự (max {max_length})"
        )
    return value
