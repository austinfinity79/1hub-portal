"""Security utilities: NAPAS signature verify + IP whitelist.

IP whitelist cho webhook: chỉ nhận notification từ NAPAS source IP.
Defense-in-depth — cộng với verify JWT + chữ ký RSA.
"""

import logging

from fastapi import Request

from app.config import settings
from app.core.exceptions import AppException

logger = logging.getLogger(__name__)


def verify_napas_signature(payload: bytes, signature: str) -> bool:
    """Verify chữ ký NAPAS trên notification.

    Trong mock mode (NAPAS_CERT_PATH trống): luôn trả True.
    Khi có cert thật: delegate sang crypto_napas.verify_napas_signature().
    """
    if not settings.NAPAS_CERT_PATH:
        # Mock mode — chưa có cert NAPAS
        return True

    from app.core.crypto_napas import verify_napas_signature as _verify
    return _verify(payload, signature)


def get_client_ip(request: Request) -> str:
    """Lấy real client IP, xử lý X-Forwarded-For nếu sau LB/proxy."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        # X-Forwarded-For: client, proxy1, proxy2 — lấy IP đầu tiên
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def verify_napas_source_ip(request: Request) -> None:
    """Kiểm tra request đến từ NAPAS source IP.

    Gọi trong webhook endpoint. Raise AppException(403) nếu IP không hợp lệ.
    Bỏ qua khi ENV=dev hoặc danh sách IP trống (chưa config).

    Lưu ý: sau NAT/proxy phải đọc đúng real IP (X-Forwarded-For).
    """
    allowed = settings.napas_allowed_ip_set
    if not allowed or settings.ENV == "dev":
        return

    client_ip = get_client_ip(request)
    if client_ip not in allowed:
        logger.warning(
            "Rejected webhook from unauthorized IP: %s (allowed: %s)",
            client_ip,
            allowed,
        )
        raise AppException(
            status_code=403,
            code="FORBIDDEN_IP",
            detail=f"Source IP {client_ip} not in NAPAS whitelist",
        )
