"""Time based one time codes. Same algorithm as Google Authenticator (TOTP, 30s, 6 digits)."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import struct
import time

STEP = 30
DIGITS = 6


def new_secret() -> str:
    return base64.b32encode(os.urandom(20)).decode("ascii").rstrip("=")


def _key_bytes(secret: str) -> bytes:
    pad = "=" * ((8 - len(secret) % 8) % 8)
    return base64.b32decode(secret.upper() + pad, casefold=True)


def totp(secret: str, at: float | None = None, offset: int = 0) -> str:
    counter = int((at if at is not None else time.time()) // STEP) + offset
    digest = hmac.new(_key_bytes(secret), struct.pack(">Q", counter), hashlib.sha1).digest()
    pos = digest[-1] & 0x0F
    number = (
        ((digest[pos] & 0x7F) << 24)
        | (digest[pos + 1] << 16)
        | (digest[pos + 2] << 8)
        | digest[pos + 3]
    )
    return f"{number % (10 ** DIGITS):0{DIGITS}d}"


def verify_totp(secret: str, code: str, at: float | None = None, window: int = 1) -> bool:
    got = "".join(ch for ch in (code or "") if ch.isdigit())
    if len(got) != DIGITS:
        return False
    now = at if at is not None else time.time()
    for i in range(-window, window + 1):
        if hmac.compare_digest(totp(secret, at=now, offset=i), got):
            return True
    return False
