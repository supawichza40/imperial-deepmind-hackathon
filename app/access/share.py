"""Signed share links. The encrypt passphrase is never in the token."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _unb64(text: str) -> bytes:
    pad = "=" * ((4 - len(text) % 4) % 4)
    return base64.urlsafe_b64decode(text + pad)


def mint(
    secret: bytes,
    *,
    folder_id: str,
    doc_id: str,
    perm: str,
    actor: str,
    ttl_seconds: int = 3600,
    now: float | None = None,
) -> str:
    if perm not in ("view", "download"):
        raise ValueError("share perm must be view or download")
    clock = time.time() if now is None else now
    body = {
        "f": folder_id,
        "d": doc_id,
        "p": perm,
        "by": actor,
        "exp": int(clock) + ttl_seconds,
    }
    payload = _b64(json.dumps(body, separators=(",", ":")).encode("utf-8"))
    sig = _b64(hmac.new(secret, payload.encode("ascii"), hashlib.sha256).digest())
    return f"{payload}.{sig}"


def open_token(secret: bytes, token: str, now: float | None = None) -> dict:
    try:
        payload, sig = token.split(".", 1)
    except ValueError as e:
        raise ValueError("bad share link") from e
    expect = _b64(hmac.new(secret, payload.encode("ascii"), hashlib.sha256).digest())
    if not hmac.compare_digest(expect, sig):
        raise ValueError("share link was altered")
    try:
        body = json.loads(_unb64(payload))
        folder_id = body["f"]
        doc_id = body["d"]
        perm = body["p"]
        exp = int(body["exp"])
    except (ValueError, TypeError, KeyError, UnicodeDecodeError) as e:
        raise ValueError("bad share link") from e
    clock = time.time() if now is None else now
    if int(exp or 0) < clock:
        raise ValueError("share link expired")
    if perm not in ("view", "download"):
        raise ValueError("share link has no permission")
    return {
        "folder_id": folder_id,
        "doc_id": doc_id,
        "perm": perm,
        "actor": body.get("by") or "guest",
        "exp": exp,
    }
