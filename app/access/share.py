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
) -> str:
    if perm not in ("view", "download"):
        raise ValueError("share perm must be view or download")
    body = {
        "f": folder_id,
        "d": doc_id,
        "p": perm,
        "by": actor,
        "exp": int(time.time()) + ttl_seconds,
    }
    payload = _b64(json.dumps(body, separators=(",", ":")).encode("utf-8"))
    sig = _b64(hmac.new(secret, payload.encode("ascii"), hashlib.sha256).digest())
    return f"{payload}.{sig}"


def open_token(secret: bytes, token: str) -> dict:
    try:
        payload, sig = token.split(".", 1)
    except ValueError as e:
        raise ValueError("bad share link") from e
    expect = _b64(hmac.new(secret, payload.encode("ascii"), hashlib.sha256).digest())
    if not hmac.compare_digest(expect, sig):
        raise ValueError("share link was altered")
    body = json.loads(_unb64(payload))
    if int(body.get("exp") or 0) < time.time():
        raise ValueError("share link expired")
    if body.get("p") not in ("view", "download"):
        raise ValueError("share link has no permission")
    return {
        "folder_id": body["f"],
        "doc_id": body["d"],
        "perm": body["p"],
        "actor": body.get("by") or "guest",
        "exp": body["exp"],
    }
