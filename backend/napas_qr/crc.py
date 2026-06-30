"""CRC-16/CCITT-FALSE theo §4.2.15 NAPAS QR Format v2.0.

Polynomial: 0x1021, Init: 0xFFFF, No reflect, No final XOR.
Input: toàn bộ chuỗi QR kết thúc bằng "6304" (chưa gồm value CRC).
Output: 4 ký tự hex viết HOA.
"""


def crc16_ccitt(data: str) -> str:
    """Tính CRC-16/CCITT-FALSE trên chuỗi ASCII.

    Args:
        data: Chuỗi QR payload (kết thúc bằng "6304").

    Returns:
        4 ký tự hex viết HOA, vd "F4E5".
    """
    crc = 0xFFFF
    for byte in data.encode("ascii"):
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc = crc << 1
            crc &= 0xFFFF  # giữ 16-bit
    return f"{crc:04X}"
