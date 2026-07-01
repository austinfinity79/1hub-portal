"""NAPAS APG chữ ký số: RSA-2048 SHA256withRSA, Base64.

Flow mới (CSR-based):
  1. 1Hub sinh RSA private key (.key PEM) + CSR
  2. Gửi CSR cho NAPAS → NAPAS ký → trả cert
  3. Dùng private key để sign payload gửi NAPAS
  4. Dùng cert NAPAS để verify chữ ký notification nhận về

# TODO[NAPAS-B1]: Cần mẫu canonical JSON + cặp payload/chữ ký từ NAPAS
#   để verify round-trip. Hiện sign/verify đúng chuẩn RSA PKCS#1 v1.5,
#   nhưng serialize JSON có thể khác (key ordering, spacing).
"""

import base64
import logging
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.x509 import load_pem_x509_certificate

from app.config import settings

logger = logging.getLogger(__name__)

# Cache loaded keys to avoid repeated disk I/O
_private_key: rsa.RSAPrivateKey | None = None
_napas_public_key: rsa.RSAPublicKey | None = None


def _load_private_key() -> rsa.RSAPrivateKey:
    """Load private key từ PEM file (.key).

    File path từ env NAPAS_PRIVATE_KEY_PATH. chmod 600, KHÔNG commit git.
    """
    global _private_key
    if _private_key is not None:
        return _private_key

    key_path = settings.NAPAS_PRIVATE_KEY_PATH
    if not key_path:
        raise RuntimeError(
            "NAPAS_PRIVATE_KEY_PATH chưa cấu hình. "
            "Sinh key: openssl genrsa -out client-privatekey.key 2048"
        )

    pem_data = Path(key_path).read_bytes()
    key = serialization.load_pem_private_key(pem_data, password=None)
    if not isinstance(key, rsa.RSAPrivateKey):
        raise ValueError(f"Key tại {key_path} không phải RSA private key")

    _private_key = key
    logger.info("Loaded NAPAS private key from %s", key_path)
    return _private_key


def _load_napas_cert_public_key() -> rsa.RSAPublicKey:
    """Load public key từ cert NAPAS ký trả về (.cer/.pem).

    Dùng để verify chữ ký trên notification NAPAS gửi về.
    """
    global _napas_public_key
    if _napas_public_key is not None:
        return _napas_public_key

    cert_path = settings.NAPAS_CERT_PATH
    if not cert_path:
        raise RuntimeError(
            "NAPAS_CERT_PATH chưa cấu hình. "
            "Cert do NAPAS ký CSR và trả về."
        )

    cert_data = Path(cert_path).read_bytes()
    cert = load_pem_x509_certificate(cert_data)
    pub_key = cert.public_key()
    if not isinstance(pub_key, rsa.RSAPublicKey):
        raise ValueError(f"Cert tại {cert_path} không chứa RSA public key")

    _napas_public_key = pub_key
    logger.info("Loaded NAPAS cert public key from %s", cert_path)
    return _napas_public_key


def sign_payload(payload: bytes) -> str:
    """Sign payload bằng private key, trả Base64 string.

    Thuật toán: RSA PKCS#1 v1.5 + SHA-256 (SHA256withRSA).
    # TODO[NAPAS-B1]: Xác nhận canonical JSON serialization rule.
    """
    private_key = _load_private_key()
    signature = private_key.sign(
        payload,
        padding.PKCS1v15(),
        hashes.SHA256(),
    )
    return base64.b64encode(signature).decode("ascii")


def verify_napas_signature(payload: bytes, signature_b64: str) -> bool:
    """Verify chữ ký NAPAS trên notification payload.

    Args:
        payload: Raw bytes của payload (canonical JSON).
        signature_b64: Base64-encoded RSA signature từ header NAPAS.

    Returns:
        True nếu chữ ký hợp lệ.

    # TODO[NAPAS-B1]: Cần mẫu thật để verify serialize đúng.
    """
    public_key = _load_napas_cert_public_key()
    signature = base64.b64decode(signature_b64)
    try:
        public_key.verify(
            signature,
            payload,
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
        return True
    except Exception:
        logger.warning("NAPAS signature verification failed", exc_info=True)
        return False


def reset_key_cache() -> None:
    """Reset cached keys — dùng khi rotate key hoặc trong tests."""
    global _private_key, _napas_public_key
    _private_key = None
    _napas_public_key = None
