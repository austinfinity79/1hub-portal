"""Core authentication utilities: password hashing, JWT, token hashing, API key crypto."""

import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Password ──────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ── JWT ───────────────────────────────────────────────────────────────

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token() -> str:
    """Generate a random 48-byte hex refresh token."""
    return secrets.token_hex(48)


def decode_access_token(token: str) -> dict:
    """Decode and validate an access token. Raises JWTError on failure."""
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])


# ── Token hashing (SHA-256) ──────────────────────────────────────────

def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


# ── API Key generation & crypto ──────────────────────────────────────

def generate_api_key() -> str:
    return "1hub_" + secrets.token_hex(24)


def hash_api_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


def _derive_aes_key() -> bytes:
    """Derive a 32-byte AES key from the master secret via SHA-256."""
    return hashlib.sha256(settings.API_KEY_MASTER_SECRET.encode()).digest()


def encrypt_api_key(key: str) -> tuple[str, str]:
    """Encrypt an API key with AES-256-GCM.

    Returns:
        (ciphertext_hex, nonce_hex)
    """
    aes_key = _derive_aes_key()
    aesgcm = AESGCM(aes_key)
    nonce = os.urandom(12)  # 96-bit nonce for GCM
    ciphertext = aesgcm.encrypt(nonce, key.encode(), None)
    return ciphertext.hex(), nonce.hex()


def decrypt_api_key(ciphertext_hex: str, nonce_hex: str) -> str:
    """Decrypt an API key from AES-256-GCM ciphertext."""
    aes_key = _derive_aes_key()
    aesgcm = AESGCM(aes_key)
    ciphertext = bytes.fromhex(ciphertext_hex)
    nonce = bytes.fromhex(nonce_hex)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode()
