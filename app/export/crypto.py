"""Passphrase encryption for private values that the user chose to encrypt.

Format (version 1), all local, no network:
  PBKDF2-HMAC-SHA256 (210000 rounds) -> 32 byte key
  AES-GCM, 12 byte nonce per item

The passphrase is never written into the download. If they forget it, that
payload cannot be opened. That is the point.
"""

from __future__ import annotations

import secrets
from base64 import b64decode, b64encode

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

KDF_ITERS = 210_000
SALT_LEN = 16
NONCE_LEN = 12
KEY_LEN = 32
VERSION = 1


def _b64(data: bytes) -> str:
    return b64encode(data).decode("ascii")


def _unb64(text: str) -> bytes:
    return b64decode(text.encode("ascii"))


def new_salt() -> bytes:
    return secrets.token_bytes(SALT_LEN)


def derive_key(passphrase: str, salt: bytes) -> bytes:
    if not passphrase:
        raise ValueError("passphrase is required to encrypt")
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LEN,
        salt=salt,
        iterations=KDF_ITERS,
    )
    return kdf.derive(passphrase.encode("utf-8"))


def encrypt_bytes(key: bytes, plaintext: bytes) -> tuple[bytes, bytes]:
    nonce = secrets.token_bytes(NONCE_LEN)
    ct = AESGCM(key).encrypt(nonce, plaintext, None)
    return nonce, ct


def decrypt_bytes(key: bytes, nonce: bytes, ciphertext: bytes) -> bytes:
    return AESGCM(key).decrypt(nonce, ciphertext, None)


def encrypt_text(key: bytes, plaintext: str) -> dict:
    nonce, ct = encrypt_bytes(key, plaintext.encode("utf-8"))
    return {"nonce_b64": _b64(nonce), "ct_b64": _b64(ct)}


def decrypt_text(key: bytes, item: dict) -> str:
    nonce = _unb64(item["nonce_b64"])
    ct = _unb64(item["ct_b64"])
    return decrypt_bytes(key, nonce, ct).decode("utf-8")


def encrypt_blob(key: bytes, data: bytes) -> dict:
    nonce, ct = encrypt_bytes(key, data)
    return {"nonce_b64": _b64(nonce), "ct_b64": _b64(ct)}


def decrypt_blob(key: bytes, item: dict) -> bytes:
    return decrypt_bytes(key, _unb64(item["nonce_b64"]), _unb64(item["ct_b64"]))
