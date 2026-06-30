"""TLV encoding/parsing theo EMVCo QR §4.1.

Mỗi data object = ID(2 chữ số) + Length(2 chữ số, zero-pad) + Value.
Length = số ký tự (KHÔNG phải byte) của Value.
"""


def tlv(tag: str, value: str) -> str:
    """Build một TLV field.

    Args:
        tag: 2-digit ID (vd "00", "38", "63").
        value: Chuỗi value (có thể chứa nested TLV).

    Returns:
        Chuỗi TLV: ID + Length(2) + Value.

    Raises:
        ValueError: Nếu tag không phải 2 chữ số hoặc value quá dài (>99 ký tự).
    """
    if len(tag) != 2 or not tag.isdigit():
        raise ValueError(f"Tag phải là 2 chữ số, nhận được: {tag!r}")
    length = len(value)
    if length > 99:
        raise ValueError(
            f"Value quá dài cho tag {tag}: {length} ký tự (max 99)"
        )
    return f"{tag}{length:02d}{value}"


def parse_tlv(data: str) -> list[tuple[str, str]]:
    """Parse chuỗi TLV thành danh sách (tag, value).

    Args:
        data: Chuỗi TLV nối tiếp nhau.

    Returns:
        List[(tag, value)].

    Raises:
        ValueError: Nếu chuỗi không hợp lệ.
    """
    result: list[tuple[str, str]] = []
    pos = 0
    while pos < len(data):
        if pos + 4 > len(data):
            raise ValueError(f"Thiếu dữ liệu tại vị trí {pos}")
        tag = data[pos : pos + 2]
        length_str = data[pos + 2 : pos + 4]
        if not length_str.isdigit():
            raise ValueError(f"Length không hợp lệ tại vị trí {pos + 2}: {length_str!r}")
        length = int(length_str)
        pos += 4
        if pos + length > len(data):
            raise ValueError(
                f"Value quá ngắn cho tag {tag}: cần {length} ký tự, còn {len(data) - pos}"
            )
        value = data[pos : pos + length]
        result.append((tag, value))
        pos += length
    return result
